# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
# nice rasa documentation https://link.springer.com/chapter/10.1007/978-1-4842-4096-0_4

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from spellchecker import SpellChecker
import requests
import csv
from collections import defaultdict
from datetime import datetime, timedelta
import pprint
from nlg.create_summarization_dict import create_dict_for_summarization,write_dictionary,DICT_FOR_SUMM_PATH #search_info,
from nlg.generate_summarization_in_dict import do_summarization_in_dict,DICT_SUM_PATH,write_in_dict
import json
import os
import inspect  # give the file information we get from an exception traceback.
import atexit


def kill_background_updates():
    os.system('pkill -9 -f run_background_updates.py')

if not os.name == 'nt': # check if system is not Windows
    atexit.register(kill_background_updates)

def get_line_info(level=1):
    return '{}:{}:{}'.format(inspect.stack()[level][1], inspect.stack()[level][2], inspect.stack()[level][3])

def debug_print(*args, **kwargs):
    print(get_line_info(2), *args, **kwargs)



iso_file = os.path.join(os.path.dirname(__file__),"iso_countries.csv")
iata_file = os.path.join(os.path.dirname(__file__),"IATA.csv")
locations_dict = dict()
airport_dict = defaultdict(dict)
background_updates = os.path.join(os.path.dirname(__file__),"background_updates.sh")

DICTIONARY_FOR_SUMMARIZATION = None
DICTIONARY_SUMMARIZED = None


# with open(DICT_FOR_SUMM_PATH) as jsonFile:
#     DICTIONARY_FOR_SUMMARIZATION = json.load(jsonFile)
# with open(DICT_SUM_PATH) as jsonFile:
#     DICTIONARY_SUMMARIZED = json.load(jsonFile)



with open(iso_file, newline='', encoding = 'utf-8') as csvfile_iso:
    isoreader = csv.reader(csvfile_iso)
    for row in isoreader:
        locations_dict[row[0].lower()] = row[2]

with open(iata_file,newline='', encoding ='utf-8') as csvfile_iata:
    iatareader = csv.reader(csvfile_iata)
    for row in iatareader:
        airport_dict[row[0].lower()] = row[1]

def update_dictionary():
    global DICTIONARY_FOR_SUMMARIZATION, DICTIONARY_SUMMARIZED
    new_dictionary = create_dict_for_summarization()
    print("Dictionary for summarization has been created")
    write_dictionary(new_dictionary)  # not necessairy could be removed
    print("Dictionary for summarization has been written")
    print("Waiting for the summary process. Takes about 5 minutes and requires only once at the first start of the server")
    DICTIONARY_FOR_SUMMARIZATION = new_dictionary
    new_summ_dict = do_summarization_in_dict(DICTIONARY_FOR_SUMMARIZATION)
    print("Dictionary with summarized texted has been created")
    DICTIONARY_SUMMARIZED = new_summ_dict
    write_in_dict(new_summ_dict)
    print("Dictionary with summarized texted has been written")
    print("The action Server is running. Chat-bot is ready to use")


# if not os.path.isfile(DICT_FOR_SUMM_PATH) or not os.path.isfile(DICT_SUM_PATH):
#     print("The dictionaries",DICT_FOR_SUMM_PATH,"and",DICT_SUM_PATH, "weren't created yet.")
#     print("Please wait a bit until the summary will be one. Don't worry, it only takes for the first run through.")
#     update_dictionary()

# else:
#     with open(DICT_FOR_SUMM_PATH) as jsonFile:
#         DICTIONARY_FOR_SUMMARIZATION = json.load(jsonFile)
#         print("DICTIONARY_FOR_SUMMARIZATION has been loaded")
#     with open(DICT_SUM_PATH) as jsonFile:
#         DICTIONARY_SUMMARIZED = json.load(jsonFile)
#         print("DICTIONARY_SUMMARIZED has been loaded")
#         print("The action Server is running. Chat-bot is ready to use")
#
# start_update()

if not os.path.isfile(DICT_FOR_SUMM_PATH) or not os.path.isfile(DICT_SUM_PATH):
    print("The dictionaries",DICT_FOR_SUMM_PATH,"and",DICT_SUM_PATH, "weren't created yet.")
    print("Please wait a bit until the summary will be one. Don't worry, it only takes for the first run through.")
    update_dictionary() # create dictionary with first run and take about 7 mins

else:
    with open(DICT_FOR_SUMM_PATH) as file:
        DICTIONARY_FOR_SUMMARIZATION = json.load(file)
        print("DICTIONARY_FOR_SUMMARIZATION has been loaded")
    with open(DICT_SUM_PATH) as file:
        DICTIONARY_SUMMARIZED = json.load(file)
        print("DICTIONARY_SUMMARIZED has been loaded")
        print("The action Server is running. Chat-bot is ready to use")

if not os.name == 'nt': # check if the system not Windows
    os.system(background_updates) # running updating process in background
else:
    print("Windows OS does not support shell script updates and will create new files but will not update it.")


assert DICTIONARY_FOR_SUMMARIZATION is not None

#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []



class ActionInfectionNumbersCountry(Action):

    def name(self) -> Text:
        return "action_infection_numbers_country"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        entities = []

        if tracker.latest_message['entities']:
            entities = tracker.latest_message['entities']
        else:
            print("accessed slot")
            country = tracker.get_slot("country")
            print(country)
        country = None
        date = None
        region = None

        for e in entities:
            if e['entity'] == 'country':
                country = e['value'].lower()
                print("country", country)
            if e['entity'] == 'date':
                date = e['value']
                print("date", date)
            if e['entity'] == 'region':
                region = e['value'].lower()
                print("region", region)

        if date == 'today':
            #date = datetime.today().strftime('%Y-%m-%d')
            #as a rule the last update is for yesterday
            date = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

        if date == 'yesterday' or None:
            date = (datetime.now() - timedelta(2)).strftime('%Y-%m-%d')


        if region is None:
            if country in locations_dict:
                PARAMS = {'iso': locations_dict[country],'date': date, 'region_province': region}
                URL = "https://covid-api.com/api/reports/total"
                r = requests.get(url=URL, params=PARAMS)
                r.raise_for_status()
                data = r.json()
                debug_print("DATA JSON: ", data)
                dispatcher.utter_message(text=f"Total confirmed cases in {country.capitalize()} are {data['data']['active']}, with {data['data']['confirmed_diff']} new cases."
                                        )

            # If the user quits during validation with exit button
            elif country == "EXIT_FORM":
                pass
            else: 
                dispatcher.utter_message("No country was specified in the previous step.")
            # else:
            #     spell = SpellChecker()
            #     if country not in locations_dict:
            #         PARAMS = {'iso': locations_dict[spell.correction(country)],'date': date,'region_province': region}
            #         print(spell.correction(country))
            #         URL = "https://covid-api.com/api/reports/total"  # gives the information just in country
            #         r = requests.get(url=URL, params=PARAMS)
            #         r.raise_for_status()
            #
            #         data = r.json()
            #         debug_print("DATA JSON: ", data)
            #         if len(data) > 0:
            #             dispatcher.utter_message(text=f"Current active confirmed cases in {country.capitalize()} are {data['data'][0]['active']}, with {data['data'][0]['confirmed_diff']} new cases."
            #                                   f" The death cases are {data['data'][0]['deaths']} with {data['data'][0]['deaths_diff']} new death cases. HERE 2")
            #
            #         else:
            #             dispatcher.utter_message(
            #                 text=f"Could not find any entries for country {country.capitalize()}, please check your spelling")


class ActionDeathNumbersCountry(Action):

    def name(self) -> Text:
        return "action_death_numbers_country"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        if tracker.latest_message['entities']:
            country = tracker.latest_message['entities'][0]["value"]
            print(country)
            print(type(country))
        else:
            country = tracker.get_slot("country").lower()
        
        print("RAN DEATHS")
        date = None
        region = None

        if date == 'today':
            # date = datetime.today().strftime('%Y-%m-%d')
            # as a rule the last update is for yesterday
            date = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

        if date == 'yesterday' or None:
            date = (datetime.now() - timedelta(2)).strftime('%Y-%m-%d')

        if region is None:
            print(country)
            if country in locations_dict:
                if not tracker.get_slot("boolean_answer"):
                    PARAMS = {'iso': locations_dict[country], 'date': date, 'region_province': region}
                    URL = "https://covid-api.com/api/reports/total"
                    r = requests.get(url=URL, params=PARAMS)
                    r.raise_for_status()
                    data = r.json()
                    debug_print("DATA JSON: ", data)
                    dispatcher.utter_message(
                        text=f"Total death cases are {data['data']['deaths']} with {data['data']['deaths_diff']} new death cases."
                )
                else:
                    if tracker.get_slot("boolean_answer") == "affirm":
                        PARAMS = {'iso': locations_dict[country], 'date': date, 'region_province': region}
                        URL = "https://covid-api.com/api/reports/total"
                        r = requests.get(url=URL, params=PARAMS)
                        r.raise_for_status()
                        data = r.json()
                        debug_print("DATA JSON: ", data)
                        dispatcher.utter_message(
                            text=f"Total death cases are {data['data']['deaths']} with {data['data']['deaths_diff']} new death cases."
                           )
            else:
                dispatcher.utter_message("No country was specified in the previous step.")
class ActionTravelRestrictions(Action):

    def name(self) -> Text:
        return "action_travel_restrictions"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message['entities']
        if not entities :
            dispatcher.utter_message(text="Oops,sorry.The information is missing. Please try another country")
            return []

        debug_print("Message:", entities)


        for e in entities:
            if e['entity'] == 'country':
                country = e['value'].lower()

        if country in airport_dict:
            airport_iata = airport_dict[country]
            PARAMS = {'airport': airport_iata}
            r = requests.get(url="https://covid-api.thinklumo.com/data", headers={"x-api-key":"e25f88c29ea2413abe14880d224c8c82"},params=PARAMS)
            r.raise_for_status()
            data = r.json()['covid_info']['entry_exit_info']
            pp = pprint.PrettyPrinter(indent=4)
            print("DATA RESTRICTION COVID INFO")
            pp.pprint(data)
            parameters = ['source', 'quarantine', 'testing', 'travel_restrictions']
            not_necessary_info = 'No summary available - please follow the link to learn more.'
            for i in data:
                for j in parameters:
                    if not_necessary_info not in i[j]:
                        collected_info = j.upper() + ' ' + ''.join(i[j])
                        dispatcher.utter_message(text=collected_info)
            print("This action is from Travel Restriction action")
        else:
            if country == "EXIT FORM":
                pass

        #     spell = SpellChecker()
        #     if country not in airport_dict:
        #         airport_iata = airport_dict[spell.correction(country)]
        #         PARAMS = {'airport': airport_iata}
        #         print(spell.correction(country))
        #         URL = "https://covid-api.thinklumo.com/data" # gives the information just in country
        #         r = requests.get(url=URL, headers={"x-api-key":"e25f88c29ea2413abe14880d224c8c82"},params=PARAMS)
        #         r.raise_for_status()
        #         data = r.json()['covid_info']['entry_exit_info']
        #         pp = pprint.PrettyPrinter(indent=4)
        #         print("DATA RESTRICTION COVID INFO")
        #         pp.pprint(data)
        #         parameters = ['source', 'quarantine', 'testing', 'travel_restrictions']
        #         not_necessary_info = 'No summary available - please follow the link to learn more.'
        #         for i in data:
        #             for j in parameters:
        #                 if not_necessary_info not in i[j]:
        #                     collected_info = j.upper() + ' ' + ''.join(i[j])
        #                     dispatcher.utter_message(text=collected_info)
        #         print("This action is from Travel Restriction action")
        #     else:
        #         dispatcher.utter_message(text=f"Could not find any entries for country {country.capitalize()}, please check your spelling")
        #
        # return []

class ActionInfectionNumbersCities(Action):

    def name(self) -> Text:
        return "action_infection_numbers_by_cities"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message['entities']
        if not entities:
            dispatcher.utter_message(text="Oops,sorry.The information is missing. Please try another country")
            return []

        debug_print("Message : ", entities)
        city = None
        URL = "https://www.trackcorona.live/api/cities/"

        for e in entities:
            if e['value'] == 'Hamburg': # because Hamburg is region and city
                r = requests.get(url=URL + 'hamburg')
                dispatcher.utter_message(
                    text=f"Current active cases in Hamburg are {r.json()['data'][0]['confirmed']} with {r.json()['data'][0]['dead']} death cases.")
                dispatcher.utter_message(text="Take care of yourself and your family")
                return []

            if e['entity'] == 'city':
                city = e['value'].lower()
                r = requests.get(url= URL + city)

        data = r.json()
        debug_print("DATA JSON: ", data)
        print("Running infection action")
        if len(data['data']) > 1:
            possible_cities = []
            for location in data['data']:
                possible_cities.append(location['location'])

            dispatcher.utter_message(text="There are multiple cities with a similar name:" + str(possible_cities))
        elif len(data['data']) == 1:
            debug_print("DATA", data)
            casenumber = data['data'][0]['confirmed']
            death_numbers = data['data'][0]['dead']
            dispatcher.utter_message(text=f"Current active cases in {city.capitalize()} are {casenumber} with {death_numbers} death cases.")
            dispatcher.utter_message(text="Take care of yourself and your family")
        else:
            dispatcher.utter_message(
                text=f"Could not find any entries for city {city.capitalize()}, please check your spelling")


# API for cites is closed.
# class ActionInfectionNumbersCities(Action):
#
#     def name(self) -> Text:
#         return "action_infection_numbers_by_cities"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         entities = tracker.latest_message['entities']
#         if not entities:
#             dispatcher.utter_message(text="Oops,sorry.The information is missing. Please try another country")
#             return []
#
#         debug_print("Message : ", entities)
#         city = None
#         URL = "https://www.trackcorona.live/api/cities/"
#
#         for e in entities:
#             if e['value'] == 'Hamburg': # because Hamburg is region and city
#                 r = requests.get(url=URL + 'hamburg')
#                 dispatcher.utter_message(
#                     text=f"Current active cases in Hamburg are {r.json()['data'][0]['confirmed']} with {r.json()['data'][0]['dead']} death cases.")
#                 dispatcher.utter_message(text="Take care of yourself and your family")
#                 return []
#
#             if e['entity'] == 'city':
#                 city = e['value'].lower()
#                 r = requests.get(url= URL + city)
#
#         data = r.json()
#         debug_print("DATA JSON: ", data)
#
#         if len(data['data']) > 1:
#             possible_cities = []
#             for location in data['data']:
#                 possible_cities.append(location['location'])
#
#             dispatcher.utter_message(text="There are multiple cities with a similar name:" + str(possible_cities))
#         elif len(data['data']) == 1:
#             debug_print("DATA", data)
#             casenumber = data['data'][0]['confirmed']
#             death_numbers = data['data'][0]['dead']
#             dispatcher.utter_message(text=f"Current active cases in {city.capitalize()} are {casenumber} with {death_numbers} death cases.")
#             dispatcher.utter_message(text="Take care of yourself and your family")
#         else:
#             dispatcher.utter_message(
#                 text=f"Could not find any entries for city {city.capitalize()}, please check your spelling")
#
#         print("This action is from Corona action")
#
#         return []

class ActionCoronaInfoSummarize(Action):

    def name(self) -> Text:
        return "action_corona_info_summarize"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message['entities']

        with open (DICT_SUM_PATH) as jsonFile:
            dispatcher.utter_message("These are the following information that I have, what do you need? \n \n")
            DICTIONARY_SUMMARIZED = json.load(jsonFile)
            for summary in DICTIONARY_SUMMARIZED.keys():
                dispatcher.utter_message(summary)

            for summary in DICTIONARY_SUMMARIZED.keys():
                print(f"\t \t {summary}")

        # for summary in DICTIONARY_SUMMARIZED.keys():
        #     dispatcher.utter_message(summary)
        print("Corona Info Summarize Action Ran")

        return []

class ActionAcSum(Action):

    def name(self) -> Text:
        return "action_ac_sum"
        # changed because of callback query to the bot when button is pressed, 1-64 bytes in Telegram

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message['entities']

        global DICTIONARY_SUMMARIZED


        with open (DICT_SUM_PATH) as jsonFile:
            DICTIONARY_SUMMARIZED = json.load(jsonFile)


        print("Summarize Action Ran")
        print(entities)
        #print(DICTIONARY_SUMMARIZED['vaccine']['vaccine_general_info'])

        summary_type = tracker.get_slot("sum")
        # changed because of callback query to the bot when button is pressed, 1-64 bytes in Telegram

        for text in DICTIONARY_SUMMARIZED[summary_type]:
            dispatcher.utter_message(text)

        return []


class ActionAcSumVac(Action):

    def name(self) -> Text:
        return "action_ac_sum_vac"
        # changed because of callback query to the bot when button is pressed, 1-64 bytes in Telegram

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message['entities']

        with open (DICT_SUM_PATH) as jsonFile:
            DICTIONARY_SUMMARIZED = json.load(jsonFile)

        vaccine_choice = tracker.get_slot("vaccine")
        vaccine_summary = DICTIONARY_SUMMARIZED["vaccine"][vaccine_choice]

        for text in vaccine_summary:
            dispatcher.utter_message(text)

class ValidateGetCountryInfectionForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_get_country_infection_form"
        #PARAMS = {'iso': locations_dict[country], 'date': date, 'region_province': region}

    def validate_country(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate country value."""
        country = tracker.latest_message["text"]
        print("Starting validating")
        print(type(country), country)
        try:
            PARAMS = {'iso': locations_dict[country.lower()]}
            URL = "https://covid-api.com/api/reports/total"
            r = requests.get(url=URL, params=PARAMS)
            r.raise_for_status()
            data_countries = r.json()
            print("Validating country")
            debug_print("DATA JSON: ", data_countries)
            return {"country": country}
        #If the country is misspelled, this will throw a key error
        except KeyError:
            if country == "EXIT FORM":
                return {"country": "EXIT_FORM"}
            else:
                print(country)
                print("EXIT FORM")
                dispatcher.utter_message("I cannot find the country given. Please check your spelling.")
                return {"country": None}


class ValidateGetCountryInfectionForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_get_country_death_form"
        #PARAMS = {'iso': locations_dict[country], 'date': date, 'region_province': region}

    def validate_country(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate country value."""
        country = tracker.latest_message["text"]
        print("Starting validating")
        print(type(country), country)
        try:
            PARAMS = {'iso': locations_dict[country.lower()]}
            URL = "https://covid-api.com/api/reports/total"
            r = requests.get(url=URL, params=PARAMS)
            r.raise_for_status()
            data_countries = r.json()
            print("Validation for country")
            return {"country": country}
        #If the country is misspelled, this will throw a key error
        except KeyError:
            if country == "EXIT FORM":
                return {"country": "EXIT_FORM"}
            else:
                print(country)
                print("EXIT FORM")
                dispatcher.utter_message("I cannot find the country given. Please check your spelling.")
                return {"country": None}

class ValidateTravelRestrictionInfectionForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_get_country_travel_restriction_form"
        #PARAMS = {'iso': locations_dict[country], 'date': date, 'region_province': region}

    def validate_country(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate country value."""
        country = tracker.latest_message["text"].lower()
        if country in airport_dict:
            print(f"Found {country}")
            return {"country": country}
        else:
            dispatcher.utter_message("Could not find the given country, please check your spelling.")
            return {"country": None}
