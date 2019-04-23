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
from .google_groups_api import GoogleGroupsAPI as GGA


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

    return response



def get_calendar_info(request, mail_address):


    status = None

    gca = GCA(mail_address).get_schedules()
    info_dict = gca[0]
    
    # 時間の抽出
    start = datetime.datetime.strptime(info_dict['start']['dateTime'][:-6], '%Y-%m-%dT%H:%M:%S')
    end = datetime.datetime.strptime(info_dict['end']['dateTime'][:-6], '%Y-%m-%dT%H:%M:%S')

    # 参加人数とメンバーの抽出
    num_attendees = len(info_dict['attendees']) -1
 
    num_attendees_rm_resource, members = get_participants(info_dict)
    
    # 会議概要の抽出
    summary = info_dict['summary']


    config = {}
    config['start'] = {'year':start.year, 'month':start.month, 'day':start.day, 'hour':start.hour, 'minute':start.minute, 'utc':info_dict['start']['dateTime']}
    config['end'] = {'year':end.year, 'month':end.month, 'day':end.day, 'hour':end.hour, 'minute':end.minute, 'utc':info_dict['end']['dateTime']}
    config['summary'] = summary
    config['attendees'] = {
            'num': num_attendees, 'num_people': num_attendees_rm_resource
            }
    json_str = json.dumps(config, ensure_ascii=False, indent=2)

    return _response_json(request=request, json_str=json_str, status=status)


def get_participants(info_dict):
    
    attendees = info_dict['attendees']
    print(attendees)
    members = []
    
    if 'displayName' in attendees and not 'resource' in attendees:
        num_temp = 0

        groupAddressList = [d.get('email') for d in attendees if d.get('displayName') and not d.get('resource')]
        for address in groupAddressList:
            members_dict = GGA().get_members(address)[0]
            num_temp = num_temp + len(members_dict)
            for groupMembers in members_dict['email']:
                members.append(groupMembers['email'].split('@')[0])
        for participants in attendees: 
            if not attendees.get('resource') and not attendees.get('displayName'):
                members.append(candidate['email'].split('@')[0])

        num_attendees_rm_resource = len(attendees) + num_temp - len(groupAddressList)  - len([d.get('resource') for d in attendees if d.get('resource')])
    
    else:
        for participants in attendees: 
            if not participants.get('resource'):
                members.append(participants['email'].split('@')[0])
            
        num_attendees_rm_resource = len(attendees) - len([d.get('resource') for d in attendees if d.get('resource')])


    return num_attendees_rm_resource, members


    
    
