#!/usr/bin/env python
from lxml import objectify
import argparse
import os
import codecs
import gzip

# init constants and vars
RAWDATADIR = 'opengov.cat/rawdata/xml/' # use 'wget -r -np http://opengov.cat/rawdata/xml/ to download files'
start = {}
end = {}
entity = {}

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
            id = int(item.id)
            e[id] = True
            if not entity.has_key(id):
                entity[id] = {
                    'nom': item.nom,
                    'resp': item.resp,
                    'dep': item.dep,
                    'iddep': item.iddep
                }

            #print f[:10], item.id, item.iddep
            if not start.has_key(id):
                start[id] = date


        # check last entities data
        for i in start.keys():
            if not e.has_key(i) and not end.has_key(i):
                end[i] = date

read()

f = codecs.open('entities.csv', encoding='utf-8', mode='a+')
f.write('id,start,end,nom,resp,dep,iddep\n')

# print csv file with ids and dates
for i in sorted(start.keys()):
    e = entity[i]
    f = codecs.open('entities.csv', encoding='utf-8', mode='a+')
    #f.write('%s,%s,%s, %s,%s,%s,%s\n' % (i, start[i], end.has_key(i) and end[i] or '', e['nom'], e['resp'], e['dep'], e['iddep']))
    f.write('%s,%s,%s,"%s","%s","%s",%s\n' % (i, start[i], end.has_key(i) and end[i] or '', e['nom'], e['resp'], e['dep'], e['iddep']))
