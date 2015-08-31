from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import SwitchList, SwitchDetailList

urlpatterns = patterns('',
     url(r'^switch/$', SwitchList.as_view(), name='home'),
     url(r'^switch/(?P<id>[0-9]+)$', SwitchDetailList.as_view(), name='detail_view'),
)
