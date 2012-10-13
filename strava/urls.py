from django.conf.urls.defaults import *

from strava.views import *

urlpatterns = patterns('',
    url(r'^$', index, name='index'),
    url(r'^(?P<club_id>\d+)/$', index),
)