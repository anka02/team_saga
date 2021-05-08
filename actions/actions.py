# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import os.path
import csv

iso_file = os.path.join(os.path.dirname(__file__),"iso_countries.csv")
locations_dict = dict()

with open(iso_file, newline='') as csvfile:
    isoreader = csv.reader(csvfile)
    for row in isoreader:
        locations_dict[row[0].lower()] = row[2]
#print(locations_dict) 

    
#print("PATH",path)
#print("FILE", __file__)
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
            
        #response = requests.get("https://api.covid19india.org/data.json").json()
        #response = requests.get("https://covid-api.com/api/reports").json()

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
       
        '''for data in response ["statewise"]: 
            state = "Maharashtra"
            if data["state"] == state.title():
                print(data)
        
        ''' 
        dispatcher.utter_message(text="Take care of yourself and your family")
        print("This action is from Corona action")
        #dispatcher.utter_message(text="Take care of yourself and your family in " + state.title())
        return []
