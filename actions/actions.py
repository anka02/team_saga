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
from spellchecker import SpellChecker
import requests
import os.path
import csv
from requests.auth import HTTPBasicAuth
from collections import defaultdict
from pprint import pprint

iso_file = os.path.join(os.path.dirname(__file__),"iso_countries.csv")
iata_file = os.path.join(os.path.dirname(__file__),"IATA.csv")
locations_dict = dict()
airport_dict = defaultdict(dict)

with open(iso_file, newline='') as csvfile_iso:
    isoreader = csv.reader(csvfile_iso)
    for row in isoreader:
        locations_dict[row[0].lower()] = row[2]

with open(iata_file,newline='') as csvfile_iata:
    iatareader = csv.reader(csvfile_iata)
    for row in iatareader:
        airport_dict[row[1].lower()][row[0].lower()] = row[2]

with open('iata_country.txt', 'wt') as out:
    pprint(airport_dict, stream=out)
#
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

        print("Message : ", entities)
        country = None
        
        for e in entities:
            if e['entity'] == 'country':
                country = e['value'].lower()
                
        #region = "Saarland"
        try:
            PARAMS = {'iso':locations_dict[country]} #,'region_province' :region}
            URL = "https://covid-api.com/api/reports/total"  # gives the information just in country
            r = requests.get(url=URL, params=PARAMS)
            r.raise_for_status()

            data = r.json()
            print("DATA JSON: ", data)

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
                dispatcher.utter_message(text=f"Could not find any entries for country {country}, please check your spelling")
        #URL = "https://covid-api.com/api/reports" #gives the information about cities and regions



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
        #online API testing tool https://reqbin.com
        
        country = None
        #city = None
        
        for e in entities:
            if e['entity'] == 'country':
                country = e['value'].lower()
                #add entity city 

        try:
            #if city == None:
            airport_iata = next(iter(airport_dict[country].items()))[1]
            PARAMS = {'airport': airport_iata} #should be taken from mapped iso and iata code airport dictionary
            r = requests.get(url="https://covid-api.thinklumo.com/data", headers={"x-api-key":"e25f88c29ea2413abe14880d224c8c82"},params=PARAMS)
            r.raise_for_status()
            data = r.json()
            print("DATA JSON: ", data)

            dispatcher.utter_message(text="Keep calm and keep distance")
            print("This action is from Travel Restriction action")
        except KeyError:
            try:
                spell = SpellChecker()
                airport_iata = next(iter(airport_dict[country].items()))[1]
                PARAMS = {'airport': airport_iata[spell.correction(country)]}
                print(spell.correction(country))
                URL = "https://covid-api.thinklumo.com/data" # gives the information just in country
                r = requests.get(url=URL, headers={"x-api-key":"e25f88c29ea2413abe14880d224c8c82"},params=PARAMS)
                r.raise_for_status()
                data = r.json()
                print("DATA JSON: ", data)
                dispatcher.utter_message(text="Keep calm and keep distance")
                print("This action is from Travel Restriction action")
                return []
            except KeyError:
                dispatcher.utter_message(text=f"Could not find any entries for country {country}, please check your spelling")

        return []