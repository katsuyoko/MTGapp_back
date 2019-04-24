
import httplib2
import os

from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage
# from oauth2client.contrib.django_util.storage import DjangoORMStorage

import datetime
import pickle

from .models import Credentials


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

    def get_credentials(self, session_key):

        credentials = Credentials.objects.filter(session_key=session_key).values()[0]
        # dict

        APPLICATION_NAME = 'Google Calendar API Python Quickstart'

        credentials = client.OAuth2Credentials(
            access_token=credentials['token'],
            client_id=credentials['client_id'],
            client_secret=credentials['client_secret'],
            refresh_token=credentials['refresh_token'],
            token_uri=credentials['token_uri'],
            scopes=credentials['scopes'],
            token_expiry=credentials['expiry'],
            user_agent=APPLICATION_NAME,
        )

        return credentials

    def get_schedules(self, session_key, events_num=3, start_time=None):

        credentials = self.get_credentials(session_key)
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)

        start = datetime.datetime.utcnow().isoformat() + 'Z' # Z indicates UTC time

        if start_time == 'today':
            yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
            start = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 15, 0, 0)
            start = start.isoformat() + 'Z'


        today = datetime.datetime.today()
        end = datetime.datetime(today.year, today.month, today.day, 15, 0, 0)
        end = end.isoformat() + 'Z'

        if start_time == 'tomorrow':
            tomorrow = today + datetime.timedelta(days=1)
            end = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 15, 0, 0)
            end = end.isoformat() + 'Z'

        print(start, end)

        eventsResult = service.events().list(
            calendarId=self.target_address, timeMin=start, timeMax=end,
            maxResults=events_num, singleEvents=True,
            orderBy='startTime').execute()
        events = eventsResult.get('items', [])

        if not events:
            return None

        return events
