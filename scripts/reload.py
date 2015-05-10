#!/usr/bin/env python
from lxml import objectify
import argparse
import os
import gzip

# init constants and vars
RAWDATADIR = 'opengov.cat/rawdata/xml/' # use 'wget -r -np http://opengov.cat/rawdata/xml/ to download files'
start = {}
end = {}

# load entities
def read():
    files = [ f for f in os.listdir(RAWDATADIR) if f.endswith('xml.gz') ]
    for f in sorted(files):
        date = f[:10]
        try:
            xml = gzip.open(os.path.join(RAWDATADIR, f), 'rb').read()
            root = objectify.fromstring(xml)
        except:
            print "Error reading", f
            continue

        # check xml data
        e = {}
        for item in root.item:
            e[item.id] = True
            #print f[:10], item.id, item.iddep
            if not start.has_key(item.id):
                start[item.id] = date

        # check last entities data
        for i in start.keys():
            if not e.has_key(i) and not end.has_key(i):
                end[i] = date

read()

# print csv file with ids and dates
for i in sorted(start.keys()):
    print '%s,%s,%s' % (i, start[i], end.has_key(i) and end[i] or '')
