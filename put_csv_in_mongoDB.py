import csv
from pymongo import MongoClient
#CSV to JSON Conversion
csvfile = open('emag_laptopuri.csv', 'r')  #you csv files
reader = csv.DictReader( csvfile )
#######
mongo_client=MongoClient('mongodb://root:parola@192.168.1.131:27017/')#connection
db=mongo_client.octoberrr #db name to be created
#db.laptopuri.drop()#name of the collection
header= ["pret", "descriere", "link"]

for each in reader:
    row={}
    for field in header:
        row[field]=each[field]
    db.laptopuri.insert(row)#name of the collection aka Table

