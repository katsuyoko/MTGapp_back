from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import httplib2
import os

from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage

import datetime
import pickle


## たぶんpython3系じゃないと動かない、、？
import argparse

class GoogleGroupsAPI():


    def __init__(self): 

        # self.flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

        self.home_dir = os.path.expanduser('~')

        # NOTE とりあえず1グループを入れてみる
        with open(os.path.join(self.home_dir, 'flags.pickle'), 'rb') as f:
            self.flags = pickle.load(f)
        # If there are no (valid) credentials available, let the user log in.
        if not self.flags or not self.flags.valid:
          if self.flags and self.flags.expired and self.flags.refresh_token:
              self.flags.refresh(Request())
          else:
              flow = InstalledAppFlow.from_client_secrets_file(
                  'credentials.json', SCOPES)
              self.flags = flow.run_local_server()
          # Save the credentials for the next run
          with open('token.pickle', 'wb') as token:
             pickle.dump(self.flags, token)

    def get_credentials_group(self):

        SCOPES = ['https://www.googleapis.com/auth/admin.directory.group.member.readonly', 'https://www.googleapis.com/auth/admin.directory.group.member', 'https://www.googleapis.com/auth/admin.directory.group.readonly', 'https://www.googleapis.com/auth/admin.directory.group']
        # CLIENT_SECRET_FILE = '/home/katsuya/workspace/client_secret.json'
        CLIENT_SECRET_FILE = os.path.join(self.home_dir, 'client_secret_group.json')
        APPLICARION_NAME = 'Google Directory API Python Quickstart'

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

    def get_members(self,groupAddress):

        credentials = self.get_credentials_group()
        http = credentials.authorize(httplib2.Http())
        service = build('admin', 'directory_v1', credentials=credentials)
        
        membersResult = service.members.list(groupKey=groupAddress)
        if 'members' in membersResult:
            members = membersResult.get('members', [])
        else:
            email = {'address':'abc'}
            emailList = []
            emailList.append(email)
            person = {}
            person['emails'] = emailList
            members = []
            members.append(person)

        return members
