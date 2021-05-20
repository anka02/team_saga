import os.path
import json
import csv
from collections import defaultdict

iso_file = os.path.join(os.path.dirname(__file__),"iso_countries.csv")
iata_file = os.path.join(os.path.dirname(__file__),"IATA.csv")
airport_dict = defaultdict(dict)
locations_dict = dict()
list_of_missing_country = []


def json_dump(myobject, newfilename):
    with open(newfilename, mode='w', encoding='utf-16') as file:
        json.dump(myobject, file)


with open(iso_file, newline='', encoding = 'utf-8') as csvfile_iso:
    isoreader = csv.reader(csvfile_iso)
    for row in isoreader:
        locations_dict[row[0].lower()] = row[2]

with open(iata_file,newline='', encoding= 'utf-8') as csvfile_iata:
    iatareader = csv.reader(csvfile_iata)
    for row in iatareader:
        airport_dict[row[1].lower()][row[0].lower()] = row[2]


count = 0
for key_country in locations_dict.keys():
    if key_country not in airport_dict.keys():
        list_of_missing_country.append(key_country)
to_add = set(list_of_missing_country)
for i in to_add:
    count += 1


json_dump(airport_dict, 'airportdict.json')
json_dump(locations_dict, 'locationsdict.json')
json_dump(list_of_missing_country, 'missinglocations.json')