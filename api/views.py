from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.core import serializers
from django.db.models import Sum, Count, Q

import os
import re
import sys
import json
import random
import collections
import csv
import random
import  datetime

import requests
from bs4 import BeautifulSoup 
import google_auth_oauthlib.flow
from oauthlib.oauth2 import MissingCodeError

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import generic

from .google_calendar_api import GoogleCalendarAPI as GCA
from .models import Credentials


class Top(LoginRequiredMixin, generic.TemplateView):
    template_name = 'api/top.html'


# @login_required
def auth(request):
    if hasattr(request.user, 'credentials'):
        return redirect('api:top')
    
    # SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
    # CLIENT_SECRET_FILE = os.path.join(os.environ['HOME'], 'client_secret.json')
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        settings.CLIENT_SECRET_FILE, settings.SCOPES
    )
    flow.redirect_uri = settings.REDIRECT_URI
    print(flow.redirect_uri)
    authorization_url, state = flow.authorization_url(
        approval_prompt='force',
        access_type='offline',
        include_granted_scopes='true',
    )
    request.session['state'] = state
    return redirect(authorization_url)


# @login_required
def callback(request):
    if hasattr(request.user, 'credentials'):
        return redirect('api:top')

    SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
    state = request.session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        settings.CLIENT_SECRET_FILE, settings.SCOPES
    )
    flow.redirect_uri = settings.REDIRECT_URI
    authorization_response = request.build_absolute_uri()
    try:
        flow.fetch_token(authorization_response=authorization_response)
    except MissingCodeError:
        pass
    else:
        Credentials.objects.create(
            token=flow.credentials.token,
            refresh_token=flow.credentials.refresh_token or '',
            token_uri=flow.credentials.token_uri,
            client_id=flow.credentials.client_id,
            client_secret=flow.credentials.client_secret,
            scopes=flow.credentials.scopes,
            user=request.user,
        )

    return redirect('api:top')


@login_required
def revoke(request):
    if hasattr(request.user, 'credentials'):
        request.user.credentials.revoke()
    return redirect('api:top')


# JSON をresponseに格納する奴
def _response_json(request, json_str, status):
    callback = request.GET.get('callback')
    if not callback:
        callback = request.POST.get('callback')

    if callback:
        json_str = "%s(%s)" %(callback, json_str)
        response = HttpResponse(
            json_str, content_type='application/javascript; charset=UTF-8', status=status)
    else:
        response = HttpResponse(
            json_str, content_type='application/javascript; charset=UTF-8', status=status)
    response['Access-Control-Allow-Origin'] = '*'
    return response


def hm2m(duration):
    """
    Args:
        duraiton (str):
            duration string like the format `1h20m`
    
    Return:
        minutes (int)
    """
    if 'h' in duration:
        # '1h20m' -> 1
        hours = int(duration.split('h')[0])
        # '1h20m' -> 20
        duration = duration.split('h')[1]
        minutes = int(duration.replace('m', ''))
        return minutes + hours*60
    else:
        minutes = int(duration.replace('m', ''))
        return minutes


def parse_topic_duration(topic_duration):
    topic_duration = re.split(', |,', topic_duration)
    n = len(topic_duration)

    if n >= 3:
        topic = ', '.join(topic_duration[:-1])
    elif n == 2:
        topic = topic_duration[0]

    minutes = hm2m(topic_duration[-1])

    return {"topic": topic, "minutes": minutes}


def get_calendar_info(request, mail_address=None):


    status = None


    if mail_address is None:
        gca = GCA().get_schedules(request.user)
    else:
        gca = GCA(mail_address).get_schedules(request.user)

    if gca is None:
        json_str = json.dumps({}, ensure_ascii=False, indent=2)

        return _response_json(request=request, json_str=json_str, status=status)

    members = []
    configs = {}
    configs['events'] = []

    for info_dict in gca:
        ## 時間の抽出
        start = datetime.datetime.strptime(info_dict['start']['dateTime'][:-6], '%Y-%m-%dT%H:%M:%S')
        end = datetime.datetime.strptime(info_dict['end']['dateTime'][:-6], '%Y-%m-%dT%H:%M:%S')

        ## プライベート設定への対処
        # NOTE とりあえず、必要なキーのあるなしで返す要素を変更するようにしてます。
        # プライベートかどうかは以下の条件分岐でできます。
        # if 'visibility' in info_dict.keys():
        #     if info_dict['visibility'] == 'private':
        #         return 
        #     else:
        #         pass


        ## 参加人数の抽出
        members = []
        if 'attendees' in info_dict.keys():
            num_attendees = 0
            for candidate in info_dict['attendees']:
                if '@zozo.com' in candidate['email']:
                    num_attendees += 1
                    members.append(candidate['email'].split('@')[0])

        elif 'organizer' in info_dict.keys():
            num_attendees = 1
            members.append(info_dict['organizer']['email'].split('@')[0])

        else:
            num_attendees = 0

        ## 会議タイトルの抽出
        if 'summary' in info_dict.keys():
            title = info_dict['summary']
        else:
            title = ""

        ## アジェンダ・要約の抽出
        if 'description' in info_dict.keys():
            soup = BeautifulSoup(info_dict['description'])

            if '<li>' in info_dict['description']:
                agenda = [e.text for e in soup.find_all('li')]

                summary = info_dict['description']
                # '<br>概要<br>会議の概要説明<br><ol><li>トピック１, 2h10m</li><li>トピック２, 10m</li><li>トピック３, 1h20m</li><li>トピック４, 20m</li></ol>'
                summary = re.split('<ol>|<ul>', summary)[0]
                # '<br>概要<br>会議の概要説明<br>'
                summary = summary.replace('<br>', '\n').strip()
                # '概要\n会議の概要説明'
            else:
                summary_agenda = [e.rstrip() for e in soup.text.split('- ')]
                summary = summary_agenda[0]
                agenda = summary_agenda[1:]

            agenda = [parse_topic_duration(top_dur) for top_dur in agenda]
            # 'topic1, 1h20m' -> {'topic': 'topic1', 'minutes': 80}

        else:
            agenda = []
            summary = ''


        config = {}
        config['start'] = {'year':start.year, 'month':start.month, 'day':start.day, 'hour':start.hour, 'minute':start.minute, 'utc':info_dict['start']['dateTime']}
        config['end'] = {'year':end.year, 'month':end.month, 'day':end.day, 'hour':end.hour, 'minute':end.minute, 'utc':info_dict['end']['dateTime']}
        config['title'] = title
        config['attendees'] = {
                'num': num_attendees,
                'members': members
                }
        config['agenda'] = agenda
        config['summary'] = summary
        configs['events'].append(config)

    json_str = json.dumps(configs, ensure_ascii=False, indent=2)

    return _response_json(request=request, json_str=json_str, status=status)


def get_item_info(request, price):

    try:
        url = "https://zozo.jp/search/?p_prie={}&dord=31"\
            .format(price)

        res = requests.get(url)
        soup = BeautifulSoup(res.content)
        items = soup.select("#searchResultList > li")
        # PR商品を除く、上位10個
        items = items[6:16]
        item = random.choice(items)

        # 商品の値段
        price = item.find('div', class_="catalog-price-amount").text

        # 商品画像のURL
        img_url = item.find('img')['data-src']
        # 画像サイズを大きくする。
        # 'https://c.imgz.jp/012/12345678/01234567B_3_D_215.jpg'
        # -> 'https://c.imgz.jp/012/12345678/01234567B_3_D_500.jpg'
        # img_url = re.sub("_[0-9]{3}.jpg", "_500.jpg", img_url)

        # ブランド
        brand = item.find('div', class_='catalog-h').text

        # 商品名
        item_detail_url = item.find('a', class_='catalog-link')['href'].lstrip('/')
        if not item_detail_url.startswith('http'):
            item_detail_url = os.path.join('https://zozo.jp', item_detail_url)
        res_detail = requests.get(item_detail_url)
        soup_detail = BeautifulSoup(res_detail.content)
        name = soup_detail.find('h1').text

        config = {}
        config['item'] = {
            'price': price,
            'img_url': img_url,
            'brand': brand,
            'name': name,
        }
        json_str = json.dumps(config, ensure_ascii=False, indent=2)

        status = None

        return _response_json(request=request, json_str=json_str, status=status)

    except:

        json_str = json.dumps({}, ensure_ascii=False, indent=2)

        return _response_json(request=request, json_str=json_str, status=None)
