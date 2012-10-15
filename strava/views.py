from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

import calendar
from datetime import datetime

from stravaapi import StravaApi

import json

METERS_TO_MILES_RATIO = 0.000621371
METERS_TO_FEET_RATIO = 3.28084

DEFAULT_CLUBS = [
    { 'id': '1', 'name': 'Team Strava' },
    { 'id': '15', 'name': 'Mission Cycling' },
]

MONTHS = [
    { 'id': 1, 'name': 'January' },
    { 'id': 2, 'name': 'February' },
    { 'id': 3, 'name': 'March' },
    { 'id': 4, 'name': 'April' },
    { 'id': 5, 'name': 'May' },
    { 'id': 6, 'name': 'June' },
    { 'id': 7, 'name': 'July' },
    { 'id': 8, 'name': 'August' },
    { 'id': 9, 'name': 'September' },
    { 'id': 10, 'name': 'October' },
    { 'id': 11, 'name': 'November' },
    { 'id': 12, 'name': 'December' },
]


def comp(request, club_id=1):
    club_details = get_club_details(club_id)

    context = RequestContext(request)
    return render_to_response('strava/comp.html',
    {
        'club_details': club_details,
        'club_options': DEFAULT_CLUBS,
        'selected_club': club_id,
        'month_options': MONTHS,
        'selected_month': datetime.now().month
    },
    context_instance=context)


def athlete_details(request, athlete_id=None, month=None):
    name = request.GET.get('name');
    athlete_details = get_athlete_details(athlete_id, month)
    athlete_details['name'] = name
    return HttpResponse(json.dumps(athlete_details), mimetype='application/json')


def club_details(request, club_id=1):
    load_athlete_details = request.GET.get('loadAthleteDetails', 'false')

    if load_athlete_details == 'true':
        load_athlete_details = True
    else:
        load_athlete_details = False

    club_details = get_club_details(club_id, load_athlete_details)
    return HttpResponse(json.dumps(club_details), mimetype='application/json')


def get_club_details(club_id, load_athlete_details=False):
    api = StravaApi()

    # Get the club.
    club = api.club_details(club_id)

    # Get the members for the club.
    club['members'] = api.club_members(club_id)

    if load_athlete_details:
        for member in club['members']:
            member['details'] = get_athlete_details(member['id'])

    return club


def get_athlete_details(athlete_id, month=None):
    now = datetime.now()

    if month is None:
        month = now.month
    else:
        month = int(month)

    date_range = calendar.monthrange(now.year, month)

    start_date = '%s-%s-%s' % (now.year, month, 1)
    end_date = '%s-%s-%s' % (now.year, month, date_range[1])

    api = StravaApi()

    # Get the athlete's rides.
    athlete = {}
    rides = api.rides(athlete_id=athlete_id, start_date=start_date, end_date=end_date)

    total_climbed = 0
    average_climbed = 0
    total_distance = 0
    average_distance = 0
    number_rides = 0

    if len(rides) > 0:
        # Need to make sure we get them all. Not many riders will have > 50 rides in a month, though.
        iteration = 1
        while len(rides) % 50 == 0:
            offset = 50 * iteration
            iteration += 1
            rides.extend(api.rides(athlete_id=athlete_id, start_date=start_date, end_date=end_date, offset=offset))

        # We need the details for each ride as well.
        for ride in rides:
            ride['details'] = api.ride_details(ride['id'])
            total_climbed += ride['details']['elevationGain'] * METERS_TO_FEET_RATIO
            total_distance += ride['details']['distance'] * METERS_TO_MILES_RATIO

        number_rides = len(rides)
        average_climbed = total_climbed / number_rides
        average_distance = total_distance / number_rides

    athlete['id'] = athlete_id
    athlete['number_rides'] = number_rides
    athlete['total_climbed'] = { 'display': round(total_climbed, 1), 'raw': total_climbed }
    athlete['average_climbed'] = { 'display': round(average_climbed, 1), 'raw': average_climbed }
    athlete['total_distance'] = { 'display': round(total_distance, 1), 'raw': total_distance }
    athlete['average_distance'] = { 'display': round(average_distance, 1), 'raw': average_distance }

    return athlete