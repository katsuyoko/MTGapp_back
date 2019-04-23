from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.core import serializers
from django.db.models import Sum, Count, Q

import sys
import json
import collections
import csv
import random
import  datetime

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
    # info_dict = gca[0]
    
    configs = {}
    configs['events'] = []

    for info_dict in gca:
        # 時間の抽出
        start = datetime.datetime.strptime(info_dict['start']['dateTime'][:-6], '%Y-%m-%dT%H:%M:%S')
        end = datetime.datetime.strptime(info_dict['end']['dateTime'][:-6], '%Y-%m-%dT%H:%M:%S')

        # 参加人数の抽出
        num_attendees = len(info_dict['attendees']) -1

        # 会議概要の抽出
        summary = info_dict['summary']


        config = {}
        config['start'] = {'year':start.year, 'month':start.month, 'day':start.day, 'hour':start.hour, 'minute':start.minute, 'utc':info_dict['start']['dateTime']}
        config['end'] = {'year':end.year, 'month':end.month, 'day':end.day, 'hour':end.hour, 'minute':end.minute, 'utc':info_dict['end']['dateTime']}
        config['summary'] = summary
        config['attendees'] = {
                'num': num_attendees,
                }
        configs['events'].append(config)

    json_str = json.dumps(configs, ensure_ascii=False, indent=2)

    return _response_json(request=request, json_str=json_str, status=status)


