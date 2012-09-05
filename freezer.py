#!/usr/bin/python
# -*- coding: utf8 -*-

import httplib2
import pprint

from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow


# Copy your credentials from the APIs Console
CLIENT_ID = '110358685167-hcaeade6erniobnfmm1t90sahcdoqa2c.apps.googleusercontent.com'
CLIENT_SECRET = '7XwCrSOXPmKmPZrRM2HNYe60'

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

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

docs = {}

while not docs or res.get("nextPageToken", False):
    if not docs:
        list = drive_service.files().list()
    else:
        list = drive_service.files().list(pageToken=res["nextPageToken"])
    res = list.execute()
    for i in res.get('items',[]):
        el = i.get('exportLinks', {})
        if i['labels']['starred'] and el.has_key('text/html'):
            docs[i['id']] = i

for id,d in docs.items():
    print "id: %s title: %s export to html url: %s " % (d['title'], id, d['exportLinks']['text/html'])
