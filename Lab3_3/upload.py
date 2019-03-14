#! /usr/bin/python3

'''
Uploads Yelp! review data to a MongoDB instance.
'''

import json
import os
import pymongo

_datapath = './data/business100ValidForm.json'

# get a mongodb connection
client = pymongo.MongoClient('mongodb://localhost:27017/')

# error checking to make sure we got a connection
if not client:
    print('Error: Unable to acquire MongoDB connection on localhost! Are you sure it is running?')
    sys.exit(1)
    
# get the database
db = client.yelp_dataset

# error checking for the database
if not db:
    print('Error: Unable to connect to the yelp_dataset database on MongoDB localhost instance!')
    sys.exit(1)
    
# get the reviews collection
reviews = db.reviews
    
# error checking for the collection
if not reviews:
    print('Error: Unable to connect to the reviews collection in the yelp_dataset collection!')
    sys.exit(1)

# read in the data from file
if not os.path.exists(_datapath):
    raise OSError
with open(_datapath, 'r') as f:
    json_data = json.load(f)['Business']
    
# try to bulk insert the database into mongodb
if reviews.insert_many(json_data):
    print('Successfully inserted records into the reviews collection.')
