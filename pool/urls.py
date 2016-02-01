from django.conf.urls import patterns, url

from views import *

urlpatterns = patterns('',
    url(r'^/pool/(?P<id>[1-9][0-9]?)$',
        PoolDetailView.as_view()),
    url(r'^/pool$',
        PoolListView.as_view()),
)
