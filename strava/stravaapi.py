from django.core.cache import cache

import httplib2
import json

BASE_URL = "http://www.strava.com/api/v1"

class StravaApi(object):
    def __init__(self):
        self.h = httplib2.Http('.cache')

    def load(self, url, index_key, method='GET'):
        #print BASE_URL + url
        resp, content = self.h.request(BASE_URL + url, method)
        data = (json.loads(content))[index_key]
        return data

    def load_from_cache(self, url, index_key, method='GET'):
        data = cache.get(url, None)
        if data is None:
            #print 'Loading %s into cache' % url
            data = self.load(url, index_key, method)
            cache.set(url, data, 600)
        #else:
            #print '%s IN CACHE ALREADY' % url

        return data

    def clubs(self, name):
        url = '/clubs'

        if name is not None:
            url += '?name=%s' % name

        return self.load_from_cache(url, 'clubs')


    def club_details(self, club_id):
        url = '/clubs/%s' % club_id
        return self.load_from_cache(url, 'club')

    def club_members(self, club_id):
        url = '/clubs/%s/members' % club_id
        return self.load_from_cache(url, 'members')

    def effort_details(self, effort_id):
        url = '/efforts/%s' % effort_id
        return self.load_from_cache(url, 'effort')

    def rides(self, club_id=None, athlete_id=None, athlete_name=None, start_date=None, end_date=None,
              start_id=None, offset=None):
        url = '/rides?'

        if club_id is not None:
            url += '&clubId=%s' % club_id

        if athlete_id is not None:
            url += '&athleteId=%s' % athlete_id

        if athlete_name is not None:
            url += '&athleteName=%s' % athlete_name

        if start_date is not None:
            url += '&startDate=%s' % start_date

        if end_date is not None:
            url += '&endDate=%s' % end_date

        if start_id is not None:
            url += '&startId=%s' % start_id

        if offset is not None:
            url += '&offset=%s' % offset

        return self.load_from_cache(url, 'rides')

    def ride_details(self, ride_id):
        url = '/rides/%s' % ride_id
        return self.load_from_cache(url, 'ride')

    def ride_efforts(self, ride_id):
        url = '/rides/%s/efforts' % ride_id
        return self.load_from_cache(url, 'efforts')

    def segment(self, segment_id):
        url = '/segments/%s' % segment_id
        return self.load_from_cache(url, 'segment')

    def segment_efforts(self, segment_id, club_id=None, athlete_id=None, athlete_name=None, start_date=None,
                        end_date=None, start_id=None, best=None):
        url = '/segments/%s/efforts?' % segment_id

        if club_id is not None:
            url += '&clubId=%s' % club_id

        if athlete_id is not None:
            url += '&athleteId=%s' % athlete_id

        if athlete_name is not None:
            url += '&athleteName=%s' % athlete_name

        if start_date is not None:
            url += '&startDate=%s' % start_date

        if end_date is not None:
            url += '&endDate=%s' % end_date

        if start_id is not None:
            url += '&startId=%s' % start_id

        if best is not None:
            url += '&best=%s' % best

        return self.load_from_cache(url, 'efforts')