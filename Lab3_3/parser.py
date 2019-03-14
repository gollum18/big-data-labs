#! /usr/bin/python3

import csv
import json
import os
import pymongo
import sys

_csvpath = './TSV/'

if not os.path.exists(_csvpath):
    os.mkdir(_csvpath)

# taken from: https://stackoverflow.com/questions/2556108/rreplace-how-to-replace-the-last-occurrence-of-an-expression-in-a-string
def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

def write_header(path, header):
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)

def write_attributes(path, business_id, attributes):
    
    def write_dict(sub_path, dictionary):
        if not os.path.exists(sub_path):
            write_header(sub_path, ['business_id', 'key', 'value'])
        with open(sub_path, 'a', newline='') as f:
            sub_writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
            for key, value in dictionary.items():
                sub_writer.writerow([business_id, key, value])
    
    if not os.path.exists(path):
        write_header(path, ['business_id', 'attribute', 'value'])
    with open(path, 'a', newline='') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        for attribute, value in attributes.items():
            if type(value) == dict:
                parts = '{0}'.format(attribute.lower()).split(' ')
                attrib_id = ''
                for part in parts:
                    attrib_id = attrib_id + part + '_'
                attrib_id = rreplace(attrib_id, '_', '', 1)
                # get the sub path
                sub_path = '{0}{1}.tsv'.format(_csvpath, attrib_id)
                write_dict(sub_path, value)
            else:
                writer.writerow([business_id, attribute, value])

def write_hours(path, business_id, hours):
    if not os.path.exists(path):
        write_header(path, ['business_id', 'day', 'close', 'open'])
    with open(path, 'a', newline='') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        for day, hour in hours.items():
            writer.writerow([business_id, day, hour['close'], hour['open']])

def write_list(path, business_id, items, item_name):
    if not os.path.exists(path):
        write_header(path, ['business_id', item_name])
    with open(path, 'a', newline='') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        for item in items:
            writer.writerow([business_id, item])

def read_from_mongo():
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
    
    yelp_data = reviews.find({}, {"_id":0})
    if not yelp_data:
        print('Error: Unable to retrieve Yelp! review data from MongoDB!')
        sys.exit(1)
        
    #print(len(yelp_data))
        
    mongo_data = []
    for review in yelp_data:
        mongo_data.append(review)
        
    return mongo_data

def write_to_tsv(mongo_data):
    if not os.path.exists(_csvpath + 'businesses.tsv'):
        with open(_csvpath + 'businesses.tsv', 'w', newline='') as f:
            writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['business_id', 'full_address', 'open', 'city', 'review_count', 
                'name', 'longitude', 'state', 'stars', 'latitude', 'type'])

    with open(_csvpath + 'businesses.tsv', 'a', newline='') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        for item in mongo_data:
            values = []
            business_id = item['business_id']
            for key, value in item.items():
                if type(value) == dict:
                    # build the path
                    path = "{0}{1}.tsv".format(_csvpath, key)
                    if key == 'hours':
                        write_hours(path, business_id, value)
                    elif key == 'attributes':
                        write_attributes(path, business_id, value)
                elif type(value) == list:
                    if key == 'categories':
                        path = _csvpath + 'categories.tsv'
                        item_name = 'category'
                    elif key == 'neighborhoods':
                        path = _csvpath + 'neighborhoods.tsv'
                        item_name = 'neighborhood'
                    write_list(path, business_id, value, item_name)
                else:
                    if type(value) == str:
                        values.append(value.replace('\n', ' '))
                    else:
                        values.append(value)
            writer.writerow([*values])

if __name__ == '__main__':
    mongo_data = read_from_mongo()
    write_to_tsv(mongo_data)
