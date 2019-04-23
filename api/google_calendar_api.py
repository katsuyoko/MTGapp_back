
import httplib2
import os

from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage

import datetime
import pickle


## たぶんpython3系じゃないと動かない、、？
import argparse

class GoogleCalendarAPI():


    def __init__(self, target_address='primary'):

        # self.target_address = target_address
        # self.flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

        self.home_dir = os.path.expanduser('~')

        # NOTE とりあえず会議室のアドレスに自動的になるようにしてます
        self.target_address = "kaya@zozo.com"
        with open(os.path.join(self.home_dir, 'flags.pickle'), 'rb') as f:
            self.flags = pickle.load(f)

    def get_credentials(self):


        SCOPES = 'https://www.googleapis.com/auth/calendar.readonry'
        # CLIENT_SECRET_FILE = '/home/katsuya/workspace/client_secret.json'
        CLIENT_SECRET_FILE = os.path.join(self.home_dir, 'client_secret.json')
        APPLICARION_NAME = 'Google Calendar API Python Quickstart'

        credential_dir = os.path.join(self.home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'calendar-python-quickstart.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICARION_NAME
            credentials = tools.run_flow(flow, store, self.flags)

        return credentials

    def get_schedules(self):

        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)

        now = datetime.datetime.utcnow().isoformat() + 'Z' # Z indicates UTC time
        eventsResult = service.events().list(
            calendarId=self.target_address, timeMin=now,
            maxResults=1, singleEvents=True,
            orderBy='startTime').execute()
        events = eventsResult.get('items', [])

        if not events:
            return '何も帰ってきてないよ'

        return events
