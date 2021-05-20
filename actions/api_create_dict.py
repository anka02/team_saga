import os.path
import csv
from collections import defaultdict

iso_file = os.path.join(os.path.dirname(__file__),"iso_countries.csv")
iata_file = os.path.join(os.path.dirname(__file__),"IATA.csv")
airport_dict = defaultdict(dict)
locations_dict = dict()

with open(iso_file, newline='') as csvfile_iso:
    isoreader = csv.reader(csvfile_iso)
    for row in isoreader:
        locations_dict[row[0].lower()] = row[2]

with open(iata_file,newline='') as csvfile_iata:
    iatareader = csv.reader(csvfile_iata)
    for row in iatareader:
        airport_dict[row[1].lower()][row[0].lower()] = row[2]

list_of_missing_country = []
count = 0
for key_cuntry in locations_dict.keys():
    if key_cuntry not in airport_dict.keys():
        list_of_missing_country.append(key_cuntry)
to_add = set(list_of_missing_country)
for i in to_add:
    count += 1


