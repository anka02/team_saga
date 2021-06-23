# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
# the normal rasa documantation https://link.springer.com/chapter/10.1007/978-1-4842-4096-0_4


# This is a simple example for a custom action which utters "Hello World!"


from typing import Any, DefaultDict, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from pathlib import Path
from spellchecker import SpellChecker
import requests
import os.path
import csv
import json
from requests.auth import HTTPBasicAuth
from collections import defaultdict
from datetime import datetime, timedelta
import pprint

from nlg.create_summarization_dict import create_dict_for_summarization,write_dictionary,DICT_FOR_SUMM_PATH #search_info,
from nlg.generate_summarization_in_dict import do_summarization_in_dict,DICT_SUM_PATH,write_in_dict
from concurrent.futures import ThreadPoolExecutor
import time
import signal
import sys
import json


iso_file = os.path.join(os.path.dirname(__file__),"iso_countries.csv")
iata_file = os.path.join(os.path.dirname(__file__),"IATA.csv")
locations_dict = dict()
airport_dict = defaultdict(dict)

DICTIONARY_FOR_SUMMARIZATION = None
DICTIONARY_SUMMARIZED = None


executor = ThreadPoolExecutor(max_workers=1)

with open(iso_file, newline='', encoding = 'utf-8') as csvfile_iso:
    isoreader = csv.reader(csvfile_iso)
    for row in isoreader:
        locations_dict[row[0].lower()] = row[2]

with open(iata_file,newline='', encoding = 'utf-8') as csvfile_iata:
    iatareader = csv.reader(csvfile_iata)
    for row in iatareader:
        airport_dict[row[1].lower()][row[0].lower()] = row[2]


# To interup update function,otherwise Ctrl+C :

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# First time the global variables DICTIONARY_FOR_SUMMARIZATION,DICTIONARY_SUMMARIZED
# need to be created. It take about 5 mins (because of summarizations). Then this dictionary
# will be dowlnoded and just every our updated
# Please add any informational message about loading the program, to .

def update_dictionary(wait = False): # Update dictionary with actual every 20 sec
    global DICTIONARY_FOR_SUMMARIZATION,DICTIONARY_SUMMARIZED
    new_dictionary = create_dict_for_summarization()
    write_dictionary(new_dictionary) # not necessairy could be removed
    DICTIONARY_FOR_SUMMARIZATION = new_dictionary
    new_summ_dict = do_summarization_in_dict(DICTIONARY_FOR_SUMMARIZATION)
    DICTIONARY_SUMMARIZED = new_summ_dict
    write_in_dict(new_summ_dict)
    if wait :
        time.sleep(3600)
    executor.submit(update_dictionary,True)
    print("UPDATE",time.time())
if not os.path.isfile(DICT_FOR_SUMM_PATH) or not os.path.isfile(DICT_SUM_PATH):
    update_dictionary()
else:
    with open(DICT_FOR_SUMM_PATH) as jsonFile:
        DICTIONARY_FOR_SUMMARIZATION = json.load(jsonFile)
    with open(DICT_SUM_PATH) as jsonFile:
        DICTIONARY_SUMMARIZED = json.load(jsonFile)
    executor.submit(update_dictionary,True)

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
            dispatcher.utter_message(text="Oops,sorry.The information is missing. Please try another country")
            return []

        #print("Message : ", entities)
        country = None
        date = None
        region = None

        for e in entities:
            if e['entity'] == 'country':
                country = e['value'].lower()
            if e['entity'] == 'date':
                date = e['value']
            if e['entity'] == 'region':
                region = e['value'].lower()
        if date == 'today':
            #date = datetime.today().strftime('%Y-%m-%d')
            #as a rule the last update is for yesterday
            date = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

        if date == 'yesterday' or None:
            date = (datetime.now() - timedelta(2)).strftime('%Y-%m-%d')


        try:
            if region == None:
                PARAMS = {'iso':locations_dict[country],'date': date,'region_province': region}
                URL = "https://covid-api.com/api/reports/total"
                r = requests.get(url=URL, params=PARAMS)
                r.raise_for_status()
                data = r.json()
                dispatcher.utter_message(text=f"Current confirmed cases in {country.capitalize()} are {data['data']['active']}, with {data['data']['confirmed_diff']} new cases.")
            else:
                URL_2 = "https://covid-api.com/api/reports"
                PARAMS_2 = {'iso' : 'DEU', 'date': date, 'region_province': region}
                r = requests.get(url=URL_2, params=PARAMS_2)
                r.raise_for_status()
                data = r.json()
                dispatcher.utter_message(text=f"Current confirmed cases in Germany in {region.capitalize()} are {data['data'][0]['active']}, with {data['data'][0]['confirmed_diff']} new cases.")
            #print("DATA JSON: ", data)

            dispatcher.utter_message(text="Take care of yourself and your family")
            print("This action is from Corona action")
        except KeyError:
            try:
                spell = SpellChecker()
                PARAMS = {'iso': locations_dict[spell.correction(country)]}
                print(spell.correction(country))
                URL = "https://covid-api.com/api/reports/total"  # gives the information just in country
                r = requests.get(url=URL, params=PARAMS)
                r.raise_for_status()

                data = r.json()
                print("DATA JSON: ", data)

                dispatcher.utter_message(text="Take care of yourself and your family")

                print("This action is from Corona action")
                return []
            except KeyError:
                dispatcher.utter_message(text=f"Could not find any entries for country {country.capitalize()}, please check your spelling")

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

        print("Message:", entities)

        country = None

        for e in entities:
            if e['entity'] == 'country':
                country = e['value'].lower()

        try:
            airport_iata = next(iter(airport_dict[country].items()))[1]
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
            #print("This action is from Travel Restriction action")
        except KeyError:
            try:
                spell = SpellChecker()
                airport_iata = next(iter(airport_dict[country].items()))[1]
                PARAMS = {'airport': airport_iata[spell.correction(country)]}
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
                #print("This action is from Travel Restriction action")
                return []
            except KeyError:
                dispatcher.utter_message(text=f"Could not find any entries for country {country}, please check your spelling")

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

        print("Message : ", entities)
        city = None

        for e in entities:
            if e['entity'] == 'city':
                city = e['value'].lower()

        URL = "https://www.trackcorona.live/api/cities/"  # gives the information just in country

        r = requests.get(url= URL + city)

        data = r.json()
        print("DATA JSON: ", data)

        if len(data['data']) > 1:
            possible_cities = []
            for location in data['data']:
                possible_cities.append(location['location'])

            dispatcher.utter_message(text="There are multiple cities with a similar name:" + str(possible_cities))
        elif len(data['data']) == 1:
            print(data)
            casenumber = data['data'][0]['confirmed']
            dispatcher.utter_message(text=f"Current cases in {city.capitalize()} are {casenumber}.")
            dispatcher.utter_message(text="Take care of yourself and your family")

        #print("This action is from Corona action")

        return []

class ActionCoronaInfoSummarize(Action):

    def name(self) -> Text:
        return "action_corona_info_summarize"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message['entities']

        file_path = Path().resolve()
        action_path = os.path.join(file_path, "actions")

        with open (os.path.join(action_path, "dict_for_summarization.json")) as summaries:
            dispatcher.utter_message("These are the following information that I have, what do you need? \n \n")
            dictionary = json.loads(summaries.read())
            for summary in dictionary.keys():
                dispatcher.utter_message(f"\t \t {summary}")

        print("Summarize Action Ran")

        return []

class ActionCoronaInfoSummarize(Action):

    def name(self) -> Text:
        return "action_access_summary"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message['entities']

        dispatcher.utter_message("RAN ACCESS")
 
        for e in entities: # e should be list of strings,because of search_info function. Please change the code if it's not the case
            base_for_summarization = DICTIONARY_SUMMARIZED[e]
            dispatcher.utter_message(text="summarization action")

        print("Summarize Action Ran")

        return []

