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
    { 'id': '7601', 'name': 'OFFTOPIC' },
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

    print load_athlete_details
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


#def index(request, club_id=None):
#    api = StravaApi()
#
#    template = 'strava/index.html'
#    if request.is_ajax():
#        template = 'strava/competition.html'
#
#    if club_id is None or club_id == 0:
#        club_id = 1
#
#    club = _get_club(club_id)
##    club = api.club_details(club_id)
##
##    club['members'] = api.club_members(club_id)
##    for member in club['members']:
##        temp = api.rides(athlete_id=member['id'], start_date='2012-10-01', end_date='2012-10-31')
##        member['rides'] = temp
##
##        iteration = 1
##        while len(temp) == 50:
##            offset = 50 * iteration
##            temp = api.rides(athlete_id=member['id'], start_date='2012-10-01', end_date='2012-10-31', offset=offset)
##            member['rides'].extend(temp)
##            iteration += 1
##
##        numberOfRides = len(member['rides'])
##        member['totalDistance'] = 0
##        member['totalClimbed'] = 0
##        for ride in member['rides']:
##            ride['details'] = api.ride_details(ride['id'])
##            member['totalDistance'] += (ride['details']['distance'] * METERS_TO_FEET_RATIO)
##            member['totalClimbed'] += (ride['details']['elevationGain'] * METERS_TO_FEET_RATIO)
##
##        member['averageGain'] = member['totalClimbed'] / numberOfRides if numberOfRides > 0 else 0
##
##    club['members'] = sorted(club['members'], key=lambda member: member['totalClimbed'], reverse=True)
#
#    context = RequestContext(request)
#    return render_to_response(template,
#    {
#        'club': club,
#        'current_club': club_id,
#        'club_options': DEFAULT_CLUBS,
#        'month_options': MONTHS,
#        'current_month': datetime.now().month,
#        'test': json.dumps(club)
#    },
#    context_instance=context)
#
#def _get_club(club_id, month=None):
#    api = StravaApi()
#
#    if month is None:
#        month = datetime.now().month
#    else:
#        month = int(month)
#
#    now = datetime.now()
#    date_range = calendar.monthrange(now.year, month)
#    print date_range
#    start_date = '%s-%s-%s' % (now.year, month, 1)#datetime.datetime(now.year, month, date_range[0])
#    end_date = '%s-%s-%s' % (now.year, month, date_range[1])#datetime.datetime(now.year, month, date_range[1])
#
#    print start_date
#
#    club = api.club_details(club_id)
#
#    club['members'] = api.club_members(club_id)
#    for member in club['members']:
#        temp = api.rides(athlete_id=member['id'], start_date=start_date, end_date=end_date)
#        member['rides'] = temp
#
#        iteration = 1
#        while len(temp) == 50:
#            offset = 50 * iteration
#            temp = api.rides(athlete_id=member['id'], start_date=start_date, end_date=end_date, offset=offset)
#            member['rides'].extend(temp)
#            iteration += 1
#
#        numberOfRides = len(member['rides'])
#        member['totalDistance'] = 0
#        member['totalClimbed'] = 0
#        for ride in member['rides']:
#            ride['details'] = api.ride_details(ride['id'])
#            member['totalDistance'] += (ride['details']['distance'] * METERS_TO_FEET_RATIO)
#            member['totalClimbed'] += (ride['details']['elevationGain'] * METERS_TO_FEET_RATIO)
#
#        member['averageGain'] = member['totalClimbed'] / numberOfRides if numberOfRides > 0 else 0
#
#    club['members'] = sorted(club['members'], key=lambda member: member['totalClimbed'], reverse=True)
#
#    return club
#
#def athlete(request, rider_id):
#    api = StravaApi()
#
#    totalElevationGained = 0
#    totalDistance = 0
#    rideEfforts = []
#
#    rides = api.rides(athlete_id=319214, start_date='2012-10-01', end_date='2012-10-30')
#    print '%s rides in October' % len(rides)
#    for ride in rides:
#        ride_details = api.ride_details(ride['id'])
#        ride_details['distance'] *= 0.000621371
#        totalDistance += ride_details['distance']
#
#        ride_efforts = api.ride_efforts(ride['id'])
#
#        ride['rideDetails'] = ride_details
#        ride['rideDetails']['elevationGain'] = 0
#        ride['efforts'] = []
#
#        for ride_effort in ride_efforts:
#            effort_details = api.effort_details(ride_effort['id'])
#
#            ride['efforts'].append(effort_details)
#            effort_details['elevationGain'] *= 3.28084
#
#            ride['rideDetails']['elevationGain'] += effort_details['elevationGain']
#
#            totalElevationGained += effort_details['elevationGain']
#
#    context = RequestContext(request)
#    return render_to_response('strava/rider.html',
#        {
#            'gain': totalElevationGained,
#            'efforts': rideEfforts,
#            'distance': totalDistance,
#            'rides': rides
#        },
#        context_instance=context)
#
#def ride(request, ride_id):
#    api = StravaApi()
#
#    ride_details = api.ride_details(ride_id)
#
#    context = RequestContext(request)
#    return render_to_response('strava/ride_details.html',
#    {
#        'ride_details': ride_details
#    }, context_instance=context)
#
#
#def athletes(request, club_id=None):
#    api = StravaApi()
#    if club_id is None:
#        club_id = int(request.GET.get('club_id'))
#
#    members = api.club_members(club_id)
#    context = RequestContext(request)
#    return render_to_response('strava/competitors_menu.html',
#        {
#            'members': members
#        },
#        context_instance=context)
#
#
#def ko(request):
#    now = datetime.now()
#    start_date = datetime(now.year, now.month, 1)
#
#    print start_date
#
#    context = RequestContext(request)
#    return render_to_response('strava/knockout.html',
#        {
#            'month_options': MONTHS,
#            'club_options': DEFAULT_CLUBS
#        }, context_instance=context)
#
#
#def competition_details(request, month=None, club_id=1):
#    club = _get_club(club_id, month)
#
#    context = RequestContext(request)
#    return render_to_response('strava/competition_details.html',
#        {
#            'club': club
#        }, context_instance=context)