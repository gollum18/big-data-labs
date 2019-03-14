#! /usr/bin/python3

import csv
import hashlib
import random
import os
import parsel
import random
import string

# define variables needed for writing the CSVs
_csv_root = './CSV/'
_bibs_fname = 'bibs.csv'
_pubs_fname = 'pubs.csv'
_authors_fname = 'authors.csv'

# used during the id generation phase of bib csv creation
_alphabet = list(string.ascii_letters +  string.digits)
# shuffle the letters
for _ in range(7):
    random.shuffle(_alphabet)

def generate_id():
    '''
    Generates a 'unique' identifier for a bibliography. These identifiers
    are used to associate papers/books with a bibliography.

    These are not supposed to be cryptographically 'secure', only that 
    they have a good chance to be unique.
    '''
    # try to get an md5 generator
    m = hashlib.md5()
    # can fail on platforms that are FIPS compliant, default to sha1 
    #   if that is the case
    if not m:
        m = haslib.sha1()
    # generate a 256 character length string
    hash_value = ''.join([random.choice(_alphabet) for _ in range(256)])
    # digest the string
    m.update(bytes(hash_value.encode('utf-8')))
    # return the digest as a string
    return m.hexdigest()

def get_name_str(first, middle, last):
    if len(middle) > 0:
        return "{0} {1} {2}".format(first, middle, last)
    else:
        return "{0} {1}".format(first, last)

def write_csv(bibs):
    '''
    Writes extracted XML data to the following CSV files:
        bibs.csv: CSV containing all bibliography information for 
            each bibliography.
        pubs.csv: CSV containing all publications listed by each 
            bibliography.
        authors.csv: CSV containing the authors listed on each 
            publication.
    Params:
        bibs: A list containing bibliography entries.
    A bibliography is a list containing a list of dictionaries where each 
    dictionary is a bibliography entry that is indexed by the following
    keys:
        publisher, title, year, authors, type, price
    Note: The author key is a dictionary as well indexed with the following
    keys:
        first-name, middle-initial, last-name, address
    In some cases, the address entry will be None (the author does not list
    an address); in other cases, the address will be a two entry tuple 
    containing first the street, then the zip code.
    '''
    try:
        # create the csv dir if it does not exist
        if not os.path.exists(_csv_root):
            os.mkdir(_csv_root)

        # manually open each csv file
        bibs_file = open(_csv_root + _bibs_fname, 'w')
        pubs_file = open(_csv_root + _pubs_fname, 'w')
        authors_file = open(_csv_root + _authors_fname, 'w')

        # create the csv objects
        bibs_writer = csv.writer(bibs_file, quoting=csv.QUOTE_MINIMAL)
        pubs_writer = csv.writer(pubs_file, quoting=csv.QUOTE_MINIMAL)
        authors_writer = csv.writer(authors_file, quoting=csv.QUOTE_MINIMAL)

        # write the headers to each file
        bibs_writer.writerow(['bib_id', 'pub_id', 'author_id', 'price'])
        pubs_writer.writerow(['pub_id', 'publisher', 'title', 'year', 'type', 'author_id'])
        authors_writer.writerow(['author_id', 'author', 'first-name', 'middle-initial', 'last-name', 'street', 'zip'])

        # loop through the bibliographies
        for bib in bibs:
            bibs_id = generate_id()
            # loop through the publications
            for pub in bib:
                pub_id = generate_id()
                pubs_base_record = []
                pubs_base_record.append(pub_id)
                pubs_base_record.append(pub['publisher'])
                pubs_base_record.append(pub['title'])
                pubs_base_record.append(str(pub['year']))
                pubs_base_record.append(pub['type'])
                author_id = None
                for author in pub['authors']:
                    # generate an author id
                    author_id = generate_id()
                    author_record = []
                    pubs_record = pubs_base_record.copy()
                    auth_name = get_name_str(author['first-name'], author['middle-initial'], author['last-name'])
                    author_record.append(auth_name)
                    author_record.append(author['first-name'])
                    author_record.append(author['middle-initial'])
                    author_record.append(author['last-name'])
                    if author['address']:
                        author_record.append(author['address'][0])
                        author_record.append(str(author['address'][1]))
                    else:
                        author_record.append('')
                        author_record.append('')
                    authors_writer.writerow([author_id, *author_record])
                    pubs_writer.writerow([*pubs_record, author_id])
                bibs_writer.writerow([bibs_id, pub_id, author_id, pub['price']])

        # remember to close them so they write out properly
        bibs_file.close()
        pubs_file.close()
        authors_file.close()
    except IOError:
        # print an error message
        print('An error occured while attempting to write the CSV files! Please try again.')
        # delete the files if they exist, since they are likely corrupt
        if os.path.exists(_csv_root + _bibs_fname):
            os.remove(_csv_root + _bibs_fname)
        if os.path.exists(_csv_root + _pubs_fname):
            os.remove(_csv_root + _pubs_fname)
        if os.path.exists(_csv_root + _authors_fname):
            os.remove(_csv_root + _authors_fname)

def get_name_tuple(name_parts):
    '''
    Gets an authors name give a tuple of name parts.
    '''
    first = name_parts[0]
    middle = name_parts[1] if len(name_parts) == 3 else ""
    last = name_parts[2 if len(name_parts) == 3 else 1]
    return (first, middle, last)

def extract_author_info(authors_sel):
    '''
    Extracts author information given an author selector.
    '''
    authors = []
    for author_sel in authors_sel:
        author = dict()
        # if there are no more elements, then are at a value node
        if int(float(author_sel.xpath("count(.//*)").get())) == 0:
            name = get_name_tuple(author_sel.xpath("./text()").get().split(' '))
            author['first-name'] = name[0]
            author['middle-initial'] = name[1]
            author['last-name'] = name[2]
        # otherwise the author contains additional elements
        else:
            # possible combinations of names include <name> and
            #   <first-name>,<last-name>
            # check for the first possibility
            if int(float(author_sel.xpath("count(.//name)").get())) > 0:
                name = get_name_tuple(author_sel.xpath(".//name/text()").get().split(' '))
                author['first-name'] = name[0]
                author['middle-initial'] = name[1]
                author['last-name'] = name[2]
            # otherwise it is the second one
            else:
                author['first-name'] = author_sel.xpath('.//first-name/text()').get()
                author['middle-initial'] = ''
                author['last-name'] = author_sel.xpath('.//last-name/text()').get()
        # pull out the authors address if it exists
        if int(float(author_sel.xpath("count(.//address)").get())) > 0:
            addr_strt = author_sel.xpath(".//street/text()").get()
            addr_zip = author_sel.xpath(".//zip/text()").get()
            author['address'] = (addr_strt, addr_zip)
        else:
            author['address'] = None
        authors.append(author)
    return authors

def extract_pub_info(pub_sel):
    '''
    Extracts publication (book/paper) information given a publication 
    selector.
    '''
    pub_info = dict()
    pub_info['publisher'] = pub_sel.xpath('.//publisher/text()').get()
    pub_info['title'] = pub_sel.xpath('.//title/text()').get()
    pub_info['year'] = pub_sel.xpath('.//year/text()').get()
    pub_info['authors'] = extract_author_info(pub_sel.xpath('.//author'))
    return pub_info

def main():
    doc = ""
    with open("bibs.xml", 'r') as xml:
        for line in xml:
            doc = doc + line.strip()

    root_selector = parsel.Selector(text=doc)

    # holds publication information
    bibs = []

    # select all of the bib elements
    for bib_root in root_selector.xpath('//bib'):
        # prime a variable to hold the publication info
        bib = []

        #select all of the book elements
        for book in bib_root.xpath('.//book'):
            pub_info = extract_pub_info(book)
            pub_info['type'] = "book"
            try:
                pub_info['price'] = book.attrib['price']
            except KeyError:
                pub_info['price'] = 0
            bib.append(pub_info)

        # select all of the paper elements
        for paper in bib_root.xpath('.//paper'):
            pub_info = extract_pub_info(paper)
            pub_info['type'] = "paper"
            try:
                pub_info['price'] = paper.attrib['price']
            except:
                pub_info['price'] = 0
            bib.append(pub_info)

        bibs.append(bib)

    # write the data to a few csv files
    write_csv(bibs)

def test():
    pass

if __name__ == '__main__':
    main()
    #test()
