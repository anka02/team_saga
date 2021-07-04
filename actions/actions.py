# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
# nice rasa documentation https://link.springer.com/chapter/10.1007/978-1-4842-4096-0_4

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
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
    print("Waiting for the summary process. Takes about 5 minutes and requires only one at the first start of the server")
    DICTIONARY_FOR_SUMMARIZATION = new_dictionary
    new_summ_dict = do_summarization_in_dict(DICTIONARY_FOR_SUMMARIZATION)
    print("Dictionary with summarized texted has been created")
    DICTIONARY_SUMMARIZED = new_summ_dict
    write_in_dict(new_summ_dict)
    print("Dictionary with summarized texted has been written")
    print("The action Server is running. Chat-bot is ready to use")

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

os.system(background_updates) # running updating process in background


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



class ActionInfectionNumbers(Action):

    def name(self) -> Text:
        return "action_infection_numbers"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message['entities']
        if not entities :
            dispatcher.utter_message(text="Oops,sorry.The information for country is missing. Please try another country")
            return []

        print("Message : ", entities)
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
                dispatcher.utter_message(text=f"Current active confirmed cases in {country.capitalize()} are {data['data']['active']}, with {data['data']['confirmed_diff']} new cases."
                                              f" The death cases are {data['data']['deaths']} with {data['data']['deaths_diff']} new death cases.")
            else:
                spell = SpellChecker()
                if country not in locations_dict:
                    PARAMS = {'iso': locations_dict[spell.correction(country)],'date': date,'region_province': region}
                    print(spell.correction(country))
                    URL = "https://covid-api.com/api/reports/total"  # gives the information just in country
                    r = requests.get(url=URL, params=PARAMS)
                    r.raise_for_status()

                    data = r.json()
                    debug_print("DATA JSON: ", data)
                    if len(data) > 0:
                        dispatcher.utter_message(text=f"Current active confirmed cases in {country.capitalize()} are {data['data'][0]['active']}, with {data['data'][0]['confirmed_diff']} new cases."
                                              f" The death cases are {data['data'][0]['deaths']} with {data['data'][0]['deaths_diff']} new death cases.")

                    else:
                        dispatcher.utter_message(
                            text=f"Could not find any entries for country {country.capitalize()}, please check your spelling")

        else:
            URL_2 = "https://covid-api.com/api/reports"
            PARAMS_2 = {'iso' : 'DEU', 'date': date, 'region_province': region}
            r = requests.get(url=URL_2, params=PARAMS_2)
            r.raise_for_status()
            data = r.json()
            print(data)
            if len(data['data']) > 0:
                dispatcher.utter_message(text=f"Current active confirmed cases in {region.capitalize()} are {data['data'][0]['active']}, with {data['data'][0]['confirmed_diff']} new cases."
                                              f" The death cases are {data['data'][0]['deaths']} with {data['data'][0]['deaths_diff']} new death cases.")

                dispatcher.utter_message(text="Take care of yourself and your family")
            else:
                dispatcher.utter_message(
                    text=f"Could not find any entries for region {region.capitalize()}, please check your spelling")
            print("This action is from Corona action")


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

        country = None

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
            spell = SpellChecker()
            if country not in airport_dict:
                airport_iata = airport_dict[spell.correction(country)]
                PARAMS = {'airport': airport_iata}
                print(spell.correction(country))
                URL = "https://covid-api.thinklumo.com/data" # gives the information just in country
                r = requests.get(url=URL, headers={"x-api-key":"e25f88c29ea2413abe14880d224c8c82"},params=PARAMS)
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
                dispatcher.utter_message(text=f"Could not find any entries for country {country.capitalize()}, please check your spelling")

        return []

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

        print("This action is from Corona action")

        return []

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

class ActionAccessSummary(Action):

    def name(self) -> Text:
        return "action_access_summary"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message['entities']

        global DICTIONARY_SUMMARIZED
        #for e in entities: # e should be list of strings,because of search_info function. Please change the code if it's not the case
            #base_for_summarization = DICTIONARY_SUMMARIZED[e]

        with open(DICT_SUM_PATH) as jsonFile:
            try:
                DICTIONARY_SUMMARIZED = json.load(jsonFile)
            except Exception as e: # to avoid the error of loading the process of writing into file
                print("Error of loading summarized_dict.json file",e)

        for information in DICTIONARY_SUMMARIZED['vaccine']['vaccine_general_info']:
            dispatcher.utter_message(text=information)
            print(information)

        print("Access Summary Action Ran")

        return []

