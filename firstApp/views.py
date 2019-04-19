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
        
        form = MailForm()
        # フォームの内容を取得する
        # とりあえず適当な奴でやりましょう
        mail_address = 'example@gmail.com'
        num_people = 5


        calender_info = self.get_calender_info(mail_address)

        d = {
            'mail_address' : mail_address,
            'num_of_people': num_people,
            'calender_info': calender_info,
        }


        return render(request, 'firstApp/confilm.html', d)

    def get_calender_info(self, mail_address):
        # カレンダーの情報を取得する奴
        pass
        start = "00:00"
        end = "01:00"

        return {'start': start, 'end': end}

class TimeDisplay(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'firstApp/time_display.html', {})



