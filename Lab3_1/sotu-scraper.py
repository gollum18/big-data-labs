#! /usr/bin/python3

'''
Author: Christen Ford
Since: 02/22/2019
Name: State of the Union Scraper

Purpose:
This script connects to the infoplease state of the union website and scrapes the speaker, date, and text of the state of the union speech for every speech on the website. Each speech is stored in a separate file; likewise, the scraper generates a master file that in addition to containing the aforementioned information on each speech, also contains the filepath to the speech on disk as well as the web address of the speech.

Notes:
This software in accordance with standards set forth by the Python Software Foundation has been written for Python 3, it will not currently function using Python2. However, if one wishes to do so, they are free to backport this software Python2.

That said, all commands (whether running the software or installing the necessary pip packages) must be done using Python3 and pip3.

certifi, parsel, and urllib3 are third party python libraries; the easiest way to acquire them is through PyPi:
    pip[3] install --user certifi parsel urllib3 (Linux/Mac)
    pip -m install --user certifi parsel urllib3 (Windows)
all other libraries used by this software are standard python libraries

License: This software is distributed AS-IS with no warranty express or implied. The author of this software assumes no responsibility for any issues that arise from its use either technical or legal. You are free to modify this software as you see fit, however it is not available for use in commercial applications. Any version of this software must retain this license verbatim.
'''

import certifi      # certificate validation
import csv          # python csv library
import logging      # error logging
import os           # directory management
import parsel       # XPath parser
import urllib3      # HTTP client

# declare variables needed later
_sotu_master_addr = 'https://www.infoplease.com/homework-help/history/collected-state-union-addresses-us-presidents'
_sotu_root_addr = 'https://www.infoplease.com/homework-help/us-documents/state-union-address-'
_speeches_txt = 'all_speeches.txt'
_speech_dir = './Speeches'
_speeches_csv = 'all_speeches.csv'

# The following snippet was taken from https://doc.scrapy.org/en/xpath-tutorial/topics/xpath-tutorial.html
#
# Below is a small "hack" to change the representation of extracted nodes when using parsel.
# This is to represent return values as serialized HTML element or
# string, and not parsel's wrapper objects.
#
parsel.Selector.__str__ = parsel.Selector.extract
parsel.Selector.__repr__ = parsel.Selector.__str__
parsel.SelectorList.__repr__ = lambda x: '[{}]'.format(
    '\n '.join("({}) {!r}".format(i, repr(s))
               for i, s in enumerate(x, start=1))
).replace(r'\n', '\n')

# create some variables for use later

def scrape():
    '''
    Part1: Create a pool and get the master web page containing links to all the speeches
    '''

    # create a request pool and get the master web page
    pool = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where())
    req = pool.request('GET', _sotu_master_addr)

    # create a parsel selector from the requests data
    parent = parsel.Selector(text=str(req.data))

    # select the span article tags that contains our data
    articles = parent.xpath('//span[contains(@class, \'article\')]').getall()

    # stores the speeches so we can write them out later
    speeches = []

    # step through each article
    for article in articles:
        '''
        Part 2: Build the file path for the speech
        '''
        # select the text from the a element
        text = parsel.Selector(article).xpath('//a/text()')[0].get()

        # lowercase the text
        text = text.lower()

        # split the text
        parts = text.split(" ")

        # conditionally treat the split words
        #   this is terrible, needs refactoring, only works
        #   because I'm fairly confident the dataset won't change
        if len(parts) == 6:  # all parts present, most common
            parts[1] = parts[1].replace(".", "")
            parts[3] = parts[3].replace("(", "")
            parts[4] = parts[4].replace(',', "")
            parts[5] = parts[5].replace(")", "")
        elif len(parts) == 5:  # no middle name, occurs a few times
            parts[2] = parts[2].replace("(", "")
            parts[3] = parts[3].replace(",", "")
            parts[4] = parts[4].replace(")", "")
        elif len(parts) == 4:  # no middle name and date, occurs once
            parts[2] = parts[2].replace("(", "")
            parts[3] = parts[3].replace(")", "")

        # build the url string and key for the dictionary
        sotu_path = ""
        for part in parts:
            # special case 1: chester's middle name is ignored in the url
            if parts[0] == "chester" and part == "a":
                continue
            sotu_path += part + "-"
        # strip of the trailing hyphen
        sotu_path = sotu_path.rstrip("-")

        '''
        Part 3: Get the speech html document and build the speech
        '''
        # for the weblink
        weblink = _sotu_root_addr + sotu_path
        # try to get the web page using the normal route
        req = pool.request('GET', weblink)
        # if the normal route failed, use the alternative route
        #   used for certain speeches where infoplease doees not use their
        #   standard address format
        if req.status == 404:
            weblink = _sotu_root_addr.replace("state-union-address-", "") + sotu_path
            req = pool.request('GET', weblink)
        # create a selector to run XPath on
        child = parsel.Selector(text=str(req.data))

        # get all the speech parts from the article div's p elements
        speech_parts = ""
        if len(parts) == 6 and parts[0] == "george" and parts[5] == "2006":
            speech_parts = child.xpath("//div[contains(@class, \'section\')]/p/text()").getall()
        else:
            speech_parts = child.xpath("//div[contains(@class, \'article\')]/p/text()").getall()

        # get the speech file name
        filelink = _speech_dir + "/" + sotu_path + ".txt"

        # build the speech
        speech = ""
        for part in speech_parts:
            # strip leading and trailing spaces since the formatting is wonked
            speech += (part.strip() + " ")
        # strip the final trailing space
        speech = speech.strip()

        # store the speech in the speeches dictionary
        # speeches are stored as tuples in the format:
        #   (name, date, filelink, weblink, speech)
        name = ""
        if len(parts) == 6:
            name = "{0} {1} {2}".format(parts[0].capitalize(), parts[1].capitalize(), parts[2].capitalize())
        else:
            name = "{0} {1}".format(parts[0].capitalize(), parts[1].capitalize())
        date = ""
        if len(parts) == 6:
            date = "{0} {1} {2}".format(parts[3].capitalize(), parts[4], parts[5])
        elif len(parts) == 5:
            date = "{0} {1} {2}".format(parts[2].capitalize(), parts[3], parts[4])
        else:
            date = "{0} {1}".format(parts[2].capitalize(), parts[3])

        # store the speech in the speeches container
        speeches.append((name, date, filelink, weblink, speech))

    return speeches

def write_to_file(speeches):
    # make the speech directory if it does not already exist
    if not os.path.exists(_speech_dir):
        os.mkdir(_speech_dir)

    # open the all_speeches file, overwrite the old file
    speeches_file = open(_speeches_txt, 'w')

    for speech in speeches:
        try:
            # write the speech to its own file
            with open(speech[2], 'w') as out:
                out.write(speech[4])

            # write the speech to the all_speeches file
            speeches_file.write(speech[4] + "\n")
        except IOError:
            logging.exception('There was an error writing the speech to file!')

    # close the all_speeches file
    speeches_file.close()

def write_to_csv(speeches):
    try:
        # write all of the speeches to the csv file
        with open(_speeches_csv, 'w') as csv_file:
            # write to the csv file
            csvwriter = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            # write the header row
            csvwriter.writerow(['Name', 'Date', 'Filelink', 'Weblink', 'Speech'])
            for speech in speeches:
                # write the speeches
                csvwriter.writerow([*speech])
    except IOError:
        logging.exception('There was an issue writing the speeches to CSV!')

# scrape the speeches, and write them to file
scraped = scrape()
write_to_file(scraped)
write_to_csv(scraped)
