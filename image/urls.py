from django.conf.urls import patterns, url

from views import *

urlpatterns = patterns('',
    url(r'^/profile/(?P<id>[1-9][0-9]?)$',
        ImageProfileDetailView.as_view()),
    url(r'^/profile$',
        ImageProfileListView.as_view()),
)
