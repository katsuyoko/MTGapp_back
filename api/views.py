from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.core import serializers
from django.db.models import Sum, Count, Q

import os
import re
import sys
import json
import collections
import csv
import random
import  datetime
import requests
from bs4 import BeautifulSoup 

from .google_calendar_api import GoogleCalendarAPI as GCA



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



def get_calendar_info(request, mail_address):


    status = None

    gca = GCA(mail_address).get_schedules()

    configs = {}
    configs['events'] = []

    for info_dict in gca:
        # 時間の抽出
        start = datetime.datetime.strptime(info_dict['start']['dateTime'][:-6], '%Y-%m-%dT%H:%M:%S')
        end = datetime.datetime.strptime(info_dict['end']['dateTime'][:-6], '%Y-%m-%dT%H:%M:%S')

        members = []
        if 'attendees' in info_dict.keys():
            num_attendees = 0
            # 参加人数の抽出
            for candidate in info_dict['attendees']:
                if '@zozo.com' in candidate['email']:
                    num_attendees += 1
                    members.append(candidate['email'].split('@')[0])
        else:
            num_attendees = 1
            members.append(info_dict['organizer']['email'].split('@')[0])

        # 会議概要の抽出
        title = info_dict['summary']

        # アジェンダの抽出
        




        config = {}
        config['start'] = {'year':start.year, 'month':start.month, 'day':start.day, 'hour':start.hour, 'minute':start.minute, 'utc':info_dict['start']['dateTime']}
        config['end'] = {'year':end.year, 'month':end.month, 'day':end.day, 'hour':end.hour, 'minute':end.minute, 'utc':info_dict['end']['dateTime']}
        config['title'] = title
        config['attendees'] = {
                'num': num_attendees,
                'menbers': members
                }
        configs['events'].append(config)

    json_str = json.dumps(configs, ensure_ascii=False, indent=2)

    return _response_json(request=request, json_str=json_str, status=status)


def get_item_info(request, price):

    p_pris = price - 100
    p_prie = price
    url = "https://zozo.jp/category/jacket-outerwear/?p_pris={}&p_prie={}"\
        .format(p_pris, p_prie)

    res = requests.get(url)
    soup = BeautifulSoup(res.content)
    items = soup.select("#searchResultList > li")
    item = items[0]

    # 商品の値段
    price = item.find('div', class_="catalog-price-amount").text

    # 商品画像のURL
    img_url = item.find('img')['data-src']
    # 画像サイズを大きくする。
    # 'https://c.imgz.jp/012/12345678/01234567B_3_D_215.jpg'
    # -> 'https://c.imgz.jp/012/12345678/01234567B_3_D_500.jpg'
    img_url = re.sub("D_[0-9]{3}.jpg", "D_500.jpg", img_url)

    # ブランド
    brand = item.find('div', class_='catalog-h').text

    # 商品名
    rel_url = item.find('a', class_='catalog-link')['href'].lstrip('/')
    item_detail_url = os.path.join('https://zozo.jp', rel_url)
    item_detail_url
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
