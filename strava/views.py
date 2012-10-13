from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

import json

import httplib2

def index(request, club_id=None):

    if club_id is None or club_id == 0:
        club_id = 1

    url = 'http://www.strava.com/api/v1/clubs/' + str(club_id)

    h = httplib2.Http('.cache')
    resp, content = h.request(url, 'GET')

    club = (json.loads(content))['club']

    context = RequestContext(request)
    return render_to_response('strava/index.html',
    {
        'club_name': club['name']
    },
    context_instance=context)