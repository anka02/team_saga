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
            
        response = requests.get("https://api.covid19india.org/data.json").json()
        #print(response)
        entities = tracker.latest_message['entities']
        
        print("Last Message Now", entities)
        #output: [{'entity': 'country', 'start': 12, 'end': 18, 'confidence_entity': 0.9983867406845093, 'value': 'france', 'extractor': 'DIETClassifier'}]
        country = None
        
        for e in entities:
            if e['entity'] == 'country':
                country = e['value'] 
                print(country)     
        for data in response ["statewise"]:
            #This API example has just Maharashtra state, we will use other API 
            # and replace the variable state with "country", I used new variable state here
            # just to be sure that API-response gives the corresponding output 
            state = "Maharashtra"
            if data["state"] == state.title():
                print(data)
        
        #dispatcher.utter_message(text="Take care of yourself and your family")
        print("This action is from Corona action")
        dispatcher.utter_message(text="Take care of yourself and your family in " + state.title())
        return []

