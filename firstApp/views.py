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

@login_required
def auth(request):
    # 既に認証済みならトップページへ
    if hasattr(request.user, 'credentials'):
        return redirect('firstApp:top')

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
    return redirect('firstApp:top')


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
