# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
# the normal rasa documantation https://link.springer.com/chapter/10.1007/978-1-4842-4096-0_4


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import os.path
import csv
from requests.auth import HTTPBasicAuth

iso_file = os.path.join(os.path.dirname(__file__),"iso_countries.csv")
locations_dict = dict()

with open(iso_file, newline='') as csvfile:
    isoreader = csv.reader(csvfile)
    for row in isoreader:
        locations_dict[row[0].lower()] = row[2]

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

class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        print("This action is from py file")
        dispatcher.utter_message(text="Text from my first hello world action")

        return []

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

        print("Last Message Now", entities)
        #output: [{'entity': 'country', 'start': 12, 'end': 18, 'confidence_entity': 0.9983867406845093, 'value': 'france', 'extractor': 'DIETClassifier'}]
        
        country = None
        
        for e in entities:
            if e['entity'] == 'country':
                country = e['value'].lower()
                print(country) 
        #region = "Saarland"
            
        PARAMS = {'iso':locations_dict[country]} #,'region_province' :region}

        #URL = "https://covid-api.com/api/reports" #gives the information about cities and regions
        
        URL = "https://covid-api.com/api/reports/total" #gives the information just in country
        r = requests.get(url=URL,params=PARAMS)
        r.raise_for_status()
        
        data = r.json()
        print("DATA JSON: ", data)
    
        dispatcher.utter_message(text="Take care of yourself and your family")
        print("This action is from Corona action")
        return []

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

        print("Last Message Now", entities)
        #online API testing tool https://reqbin.com
        PARAMS = {'airport':'TXL'} #should be taken from mapped iso and iata code airport dictionary
        r = requests.get(url="https://covid-api.thinklumo.com/data", headers={"x-api-key":"e25f88c29ea2413abe14880d224c8c82"},params=PARAMS)
       
        r.raise_for_status()
        
        data = r.json()
        print("DATA JSON: ", data)

        dispatcher.utter_message(text="Stay safe")
        print("This action is from Restriction action")

        return []
