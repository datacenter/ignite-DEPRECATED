from django.conf.urls import patterns, url

from views import *

urlpatterns = patterns('',
    url(r'^/configletindex/(?P<cfgindex_id>[1-9][0-9]*)/configlet/(?P<cfg_id>[1-9][0-9]*)/(?P<new_version>[a-zA-Z]*)$', ConfigletDetail.as_view()),
    url(r'^/configletindex/(?P<cfgindex_id>[1-9][0-9]*)/(?P<new_version>[a-zA-Z]*)$', ConfigletIndexDetail.as_view()),
    url(r'^/configletindex$', ConfigletIndex.as_view()),
    url(r'^/profileindex/(?P<prindex_id>[1-9][0-9]*)/profile/(?P<pr_id>[1-9][0-9]*)$', ProfileDetail.as_view()),
    url(r'^/profileindex/(?P<prindex_id>[1-9][0-9]*)$', ProfileIndexDetail.as_view()),
    url(r'^/profileindex$', ProfileIndex.as_view()),
    url(r'^/allprofiles$', AllProfiles.as_view())
)
