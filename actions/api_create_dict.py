import os.path
import csv
from collections import defaultdict

iso_file = os.path.join(os.path.dirname(__file__),"iso_countries.csv")
iata_file = os.path.join(os.path.dirname(__file__),"IATA.csv")
airport_dict = defaultdict(dict)
locations_dict = dict()

with open(iso_file, newline='', encoding = "utf-8") as csvfile_iso:
    isoreader = csv.reader(csvfile_iso)
    for row in isoreader:
        locations_dict[row[0].lower()] = row[2]

with open(iata_file,newline='', encoding = "utf-8") as csvfile_iata:
    iatareader = csv.reader(csvfile_iata)
    for row in iatareader:
        airport_dict[row[0].lower()] = row[1]

list_of_missing_country = []
count = 0
for key_country in locations_dict.keys():
    if key_country not in airport_dict.keys():
        list_of_missing_country.append(key_country)
to_add = set(list_of_missing_country)
for i in to_add:
    count += 1


