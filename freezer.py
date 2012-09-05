#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import httplib2
import urllib2
import pprint
import json
import codecs

from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
import pystache

import views

# Copy your credentials from the APIs Console
CLIENT_ID = '110358685167-hcaeade6erniobnfmm1t90sahcdoqa2c.apps.googleusercontent.com'
CLIENT_SECRET = '7XwCrSOXPmKmPZrRM2HNYe60'

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

try:
    res=json.load(open("list.json"))
except IOError:
    # Run through the OAuth flow and retrieve credentials
    flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE)
    authorize_url = flow.step1_get_authorize_url('urn:ietf:wg:oauth:2.0:oob')
    print 'Go to the following link in your browser: ' + authorize_url
    code = raw_input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)

    # Create an httplib2.Http object and authorize it with our credentials
    http = httplib2.Http()
    http = credentials.authorize(http)

    drive_service = build('drive', 'v2', http=http)

    list = drive_service.files().list(maxResults=1000)
    res = list.execute()
    f=open("list.json","w")
    json.dump(res,f)
    f.close()

docs = {}
folders = {}
for i in res.get('items',[]):
    print "looping on: %s" % i['title']
    mime_type = i['mimeType']
    if mime_type == "application/vnd.google-apps.folder":
        folders[i['id']] = i
    else:
        el = i.get('exportLinks', {})
        if i['labels']['starred'] and el.has_key('text/html'):
        # if el.has_key('text/html'):
            docs[i['id']] = i

out = []
for id,d in docs.items():
    url = d['exportLinks']['text/html']
    file_name = "%s.html" % id
    if not os.path.isfile("build/"+file_name):
        html = urllib2.urlopen(url).read()
        out_f = open("build/"+file_name,"w")
        out_f.write(html)
        out_f.close()

    d_out = dict (title = d['title'],
                  url = file_name,
                  source_url = d['alternateLink'],
                  )
    parents = d.get('parents', [])
    for p in parents:
        p_id = p['id']
        if not folders.has_key(p_id):
            continue
        try:
            out_index = folders[p_id].get('out_index', False)
        except KeyError:
            print "couldn't find %s in `folders`" % p_id

        if not out_index:
            folders[p_id]['out_index'] = out_index = len(out)
            out.append(dict(title=folders[p_id]['title'],
                            children=[],
                           )
                      )

        out[out_index]['children'].append(d_out)

doc_view = views.Doc(out)
renderer = pystache.Renderer()
# index = codecs.open('build/index.html', encoding='utf-8', mode='w')
index = open('build/index.html', mode='w')
index.write(renderer.render(doc_view).encode('utf8'))
