
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

        self.target_address = target_address
        self.home_dir = os.path.expanduser('~')

        # NOTE とりあえず会議室のアドレスに自動的になるようにしてます
        # self.target_address = "zozo.com_343538343931333532@resource.calendar.google.com"
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

    def get_schedules(self, events_num=3):

        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)

        utc_now = datetime.datetime.utcnow().isoformat() + 'Z' # Z indicates UTC time
        now = datetime.datetime.now()
        today = datetime.datetime.today()
        utc_end = datetime.datetime(today.year, today.month, today.day, 15, 0, 0)
        utc_end = utc_end.isoformat() + 'Z'

        print(utc_now)
        print(utc_end)
        eventsResult = service.events().list(
            calendarId=self.target_address, timeMin=utc_now, timeMax=utc_end,
            maxResults=events_num, singleEvents=True,
            orderBy='startTime').execute()
        events = eventsResult.get('items', [])

        if not events:
            return None

        return events
