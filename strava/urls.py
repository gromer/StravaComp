from django.conf.urls.defaults import *

from strava.views import *

urlpatterns = patterns('',
    url(r'^comp/$', comp),
    url(r'^comp/(?P<club_id>\d+)/$', comp),
    url(r'^athlete/$', athlete_details),
    url(r'^athlete/(?P<athlete_id>\d+)/$', athlete_details),
    url(r'^athlete/(?P<athlete_id>\d+)/(?P<month>\d+)/$', athlete_details),
    url(r'^club/$', club_details),
    url(r'^club/(?P<club_id>\d+)/$', club_details),
)