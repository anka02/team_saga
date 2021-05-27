import os.path
import csv
from collections import defaultdict
import pprint
import requests
import json

iata_file = os.path.join(os.path.dirname(__file__),"IATA.csv")
airport_dict = defaultdict(dict)
list_of_airport = list()
restriction_dict = dict()

with open(iata_file,newline='') as csvfile_iata:
    iatareader = csv.reader(csvfile_iata)
    for row in iatareader:
        airport_dict[row[1].lower()][row[0].lower()] = row[2]
with open('airport_dict.json','w') as fp:
    json.dump(airport_dict, fp)

for key,value in airport_dict.items():
    for key_2,value_2 in airport_dict[key].items():
        list_of_airport.append(value_2)

pp = pprint.PrettyPrinter(indent=4)

for iata_code in list_of_airport:
    PARAMS = {'airport': iata_code}
    if len(iata_code) == 3:
        r_1 = requests.get(url="https://covid-api.thinklumo.com/data",
                             headers={"x-api-key": "e25f88c29ea2413abe14880d224c8c82"}, params=PARAMS)
        data_covid_and_entry_exit_info = r_1.json()
        if data_covid_and_entry_exit_info != {'error': f'Airport code {iata_code} not found. Try 3-letter IATA codes, e.g., BOS.'}:
            print(iata_code,data_covid_and_entry_exit_info)
            if data_covid_and_entry_exit_info['covid_info']['entry_exit_info'] != None:
                restriction_dict[iata_code] = data_covid_and_entry_exit_info['covid_info']['entry_exit_info']
with open('restriction_dict.json','w') as fp:
    json.dump(restriction_dict, fp)

pp = pprint.PrettyPrinter(indent=4)
list_of_paremeters = ['quarantine','testing','travel_restrictions']
dict_filtered = defaultdict(list)

with open('restriction_dict.json') as json_file:
    dict_to_parse = json.load(json_file)
    pp.pprint(dict_to_parse)

for key in dict_to_parse.keys():
    print("KEY",key)
    for i in dict_to_parse[key]:
        print("INFO",i)
        for param in list_of_paremeters:
            if i[param] != 'No summary available - please follow the link to learn more.':
                dict_filtered[key].append(i[param])
for key,value in dict_filtered.items():
    lenght = 0
    for elem in dict_filtered[key]:
        lenght += len(elem.split())
    dict_filtered[key].append(lenght)

#pp.pprint(dict_filtered)

with open('dict_filtered.json','w') as fp:
    json.dump(dict_filtered, fp)

list_of_lenght = list()
for key,value in dict_filtered.items():
    list_of_lenght.append(dict_filtered[key][-1])
    if dict_filtered[key][-1] == 534:
        print("AIRPORT",key,"MAX",dict_filtered[key])
    if dict_filtered[key][-1] == 25:
        print("AIRPORT",key,"MIN",dict_filtered[key])
print(list_of_lenght)
print("MAX",max(list_of_lenght)) #MAX 534
print("MIN",min(list_of_lenght)) #MIN 25
