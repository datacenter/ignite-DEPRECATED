from django.conf.urls import patterns, url

from views import *

urlpatterns = patterns('',
    url(r'^/configlet/(?P<id>[1-9][0-9]*)$', ConfigletDetail.as_view()),
    url(r'^/configlet$', ConfigletList.as_view()),
    url(r'^/profile/(?P<id>[1-9][0-9]*)$', ProfileDetail.as_view()),
    url(r'^/profile$', ProfileList.as_view()),
)
