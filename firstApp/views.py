import google_auth_oauthlib.flow
from oauthlib.oauth2 import MissingCodeError

from django.conf import settings
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
from datetime import datetime, timedelta

from .forms import *
from .models import Credentials

# from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class Top(LoginRequiredMixin, generic.TemplateView):
    """トップページ"""
    template_name = 'firstApp/top.html'

class Top2(LoginRequiredMixin, View):
    """トップページ"""
    def get(self, request, *args, **kwargs):

        info = request.session['credentials']

        d = {
            'info':info
        }

        return render(request,'firstApp/top2.html',d)

class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'firstApp/login.html'

class Logout(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""
    template_name = 'firstApp/logout.html'

@login_required
def auth(request):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_id.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


@login_required
def callback(request):
    # 既に認証済みならトップページへ
    if hasattr(request.user, 'credentials'):
        return redirect('firstApp:top')

    state = request.session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        settings.CLIENT_SECRET, settings.SCOPES, state=state
    )
    flow.redirect_uri = settings.REDIRECT_URI
    authorization_response = request.build_absolute_uri()
    try:
        flow.fetch_token(authorization_response=authorization_response)
    except MissingCodeError:
        # 直接/callback へアクセスされた場合は、ここ
        pass
    else:
       request.session['credentials'] = {
            'token': flow.credentials.token,
            'refresh_token': flow.credentials.refresh_token,
            'token_uri': flow.credentials.token_uri,
            'client_id': flow.credentials.client_id,
            'client_secret': flow.credentials.client_secret,
            'scopes': flow.credentials.scopes,
        }
    return redirect('firstApp:top2')


@login_required
def revoke(request):
    # 認証済みアカウントならば、認証情報の取り消し
    if 'credentials' in request.session:
        credentials = google.oauth2.credentials.Credentials(**request.session['credentials'])
        requests.post(
            'https://accounts.google.com/o/oauth2/revoke',
            params={'token': credentials.token},
            headers={'content-type': 'application/x-www-form-urlencoded'}
        )
        del request.session['credentials']  # セッションも破棄する
    return redirect('firstApp:top')


def get(request):
    # 既に認証済みならトップページへ
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        settings.CLIENT_SECRET, settings.SCOPES
    )
    flow.redirect_uri = settings.REDIRECT_URI
    authorization_url, state = flow.authorization_url(
        approval_prompt='force',
        access_type='offline',
        include_granted_scopes='true')
    request.session['state'] = state
    return redirect(authorization_url)
