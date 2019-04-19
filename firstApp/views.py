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



