from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.forms import formset_factory
from django.db.models import Count
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views import generic, View
from django.utils.safestring import mark_safe

import random
import datetime
from datetime import timedelta

from .forms import *

class Top(LoginRequiredMixin, generic.TemplateView):
    """トップページ"""
    template_name = 'firstApp/top.html'

class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'firstApp/login.html'

class Logout(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""
    template_name = 'firstApp/logout.html'


class InputMailAddress(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        input_form = MailForm()

        d = {
            'form':input_form
            }

        return render(request, 'firstApp/input_mail_address.html', d)


class Confilm(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        """ 多分何もすることない """
        pass
        return None

    def post(self, request, *args, **kwargs):
        """ POSTのリクエストが来たとき """
        """ 多分メールアドレスが入力されたときの処理になる """

        form = MailForm(request.POST)
        # フォームの内容を取得する
        # とりあえず適当な奴でやりましょう
        if form.is_valid():
            mail_address = form.cleaned_data['mail_address']

            gca = GoogleCalendarAPI(mail_address).get_schedules()

            calender_info = self.get_calender_info(gca)

            d = {
                'mail_address' : mail_address,
                'calendar_info': calender_info,
            }


            return render(request, 'firstApp/confilm.html', d)

    def get_calender_info(self, gca):
        # カレンダーの情報を取得する奴
        # start = "00:00"
        # end = "01:00"

        info_dict = gca[0]

        # 時間の抽出
        start = datetime.datetime.strptime(info_dict['start']['dateTime'][:-6], '%Y-%m-%dT%H:%M:%S')
        end = datetime.datetime.strptime(info_dict['end']['dateTime'][:-6], '%Y-%m-%dT%H:%M:%S')

        # 参加人数の抽出
        num_attendees = len(info_dict['attendees']) -1

        # 会議概要の抽出
        summary = info_dict['summary']

        return {'start': start, 'end': end, 'num_attendees': num_attendees, 'summary' : summary}

class TimeDisplay(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'firstApp/time_display.html', {})



# from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage

import pickle


## たぶんpython3系じゃないと動かない、、？
import argparse

class GoogleCalendarAPI():


    def __init__(self, target_address='primary'):

        # self.target_address = target_address
        # self.flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()


        # NOTE とりあえず会議室のアドレスに自動的になるようにしてます
        self.target_address = "zozo.com_343538343931333532@resource.calendar.google.com"
        home_dir = os.path.expanduser('~')
        with open(os.path.join(home_dir, 'flags.pickle'), 'rb') as f:
            self.flags = pickle.load(f)

    def get_credentials(self):

        SCOPES = 'https://www.googleapis.com/auth/calendar.readonry'
        # CLIENT_SECRET_FILE = '/home/katsuya/workspace/client_secret.json'
        CLIENT_SECRET_FILE = '/home/katsuya/workspace/client_id.json'
        APPLICARION_NAME = 'Google Calendar API Python Quickstart'

        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
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


