#!/usr/bin/env python
from lxml import objectify
import argparse
import mechanize
import hashlib
import urlparse
from bs4 import BeautifulSoup
from yattag import Doc, indent
import os
import codecs
import httplib2
import sys
#import re

# init constants and vars
URL = 'http://sac.gencat.cat/sacgencat/AppJava/organisme_fitxa.jsp?codi=%i'
XML = 'unitatssac.xml'
IDS = 'ids.txt'
CACHEDIR = 'cache'
ENTITIES = {}
ENTITIESNAME = {}


# setup entities
def init():
    data = open(XML).read()
    root = objectify.fromstring(data)
    for item in root.item:
        ENTITIES[str(item.id)] = str(item.iddep)
        ENTITIESNAME[str(item.id)] = item.dep

# get page from gencat and cache it!
def get_page(page):
    br = mechanize.Browser()
    br.open(URL % page)

    # is an error in response?
    try:
        resp = br.response()
    except HTTPError, e:
        print "Got error code", e.code
        return

    # is an error page?
    if 'error' in br.title().lower():
        open(IDS, 'a').write('%s\n' % page)
        return

    html = resp.read()
    h = hashlib.sha1(html).hexdigest()

    # check if page has got an id
    soup = BeautifulSoup(html)
    meta = dict([ i.attrs['name'], i.attrs['content'] ] for i in soup.findAll(name="meta") if i.has_attr('name'))
    try:
        # TODO: unify these lines with get_data_from_page function
        href = soup.findAll('h3')[0].parent.parent.findNext('a', href=True)['href']
        url = urlparse.urlparse(href)
        params = urlparse.parse_qs(url.query)
        id = params['codi'][0]
    except:
        open(IDS, 'a').write('%s\n' % page)
        return

    d = '%s/%s' % (CACHEDIR, id)
    f = '%s/%s' % (d, h)

    # check dir and create it if it doesn't exist
    if not os.path.exists(d):
        os.makedirs(d)

    # check if exist and it has the same hash
    if os.path.isfile(f):
        hh = hashlib.sha1(open(f).read()).hexdigest()
        if hh != h:
            print "Change found -> ", id
            open(f, 'w').write(html)
        else:
            # same page in cache so do nothing
            return
    else:
        open(f, 'w').write(html)

    # link latest
    os.symlink(h, '%s/latest' % d)

# get data from page
def get_data_from_page(page):
    html = open('%s/%s' % (CACHEDIR, page)).read()
    soup = BeautifulSoup(html)
    meta = dict([ i.attrs['name'], i.attrs['content'] ] for i in soup.findAll(name="meta") if i.has_attr('name'))
    href = soup.findAll('h3')[0].parent.parent.findNext('a', href=True)['href']
    url = urlparse.urlparse(href)
    params = urlparse.parse_qs(url.query)
    id = params['codi'][0]

    if params.has_key('codi'):
        if ENTITIES.has_key(id):
            item = {
                'id': id,
                #'nom': '<![CDATA[%s]]>' % meta['nomorganisme'],
                'nom': meta['nomorganisme'],
                'resp': meta['responsable'] or 'null',
                'iddep': ENTITIES[id],
                'dep': ENTITIESNAME[id].text,
                'centers': ''
            }
        else:
            item = {}
    else:
        item = {}
    return item


# show XML photography
def show_xml():
    pages = [ f for f in os.listdir(CACHEDIR) if os.path.isdir(os.path.join(CACHEDIR,f)) ]

    doc, tag, text = Doc().tagtext()
    doc.asis('<?xml version="1.0" encoding="utf-8" ?>')

    # xml tags
    with tag('sac_uo'):
        for p in pages:
            item = get_data_from_page('%s/latest' % p)
            if item:
                with tag('item'):
                    with tag('id'):
                        text(item['id'])
                    with tag('nom'):
                        text(item['nom'])
                    with tag('resp'):
                        text(item['resp']) # mini hack
                    with tag('iddep'):
                        text(item['iddep'])
                    with tag('dep'):
                        text(item['dep'])
                    with tag('centers'):
                        text(item['centers'])

    return indent(
        doc.getvalue(),
        indentation = ' ' * 4,
        newline = '\r\n'
    )


# main function
if __name__ == '__main__':
    # start
    init()

    # args parse for CLI
    parser = argparse.ArgumentParser(
        description='opengov.cat initial "catcher" for seismometer [GENCAT edition].\
        See http://opengov.cat/sismograf/')
    parser.add_argument('--xml', action="store_true", default=False)
    parser.add_argument('--page', action="store", type=int, dest="page")
    args = parser.parse_args()

    if not args.page and not args.xml:
        print "Use -h or --help to get a brief description for this command"

    # check args
    if args.page:
        # check if page exists (invalid: they are responding 200 for error)
        #h = httplib2.Http()
        #h.follow_redirects = False
        #resp, body = h.request(URL % args.page, 'GET')
        #sys.exit()
        get_page(args.page)
    elif args.xml:
        xml = show_xml()
        f = codecs.open('today.xml', encoding='utf-8', mode='w+')
        f.write(xml)
