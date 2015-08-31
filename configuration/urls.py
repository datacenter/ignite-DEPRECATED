__author__  = "Rohit N Dubey"

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from views import ConfigletList,ConfigletDetail,ConfigurationList,ConfigurationDetail

urlpatterns = patterns('',
    # Examples:
     url(r'^$',ConfigurationList.as_view(), name='configuration_home'),
     url(r'^(?P<id>\w+)$', ConfigurationDetail.as_view(), name='configuration_detail_view'),
     url(r'^configlet/$',ConfigletList.as_view(), name='home'),
     url(r'^configlet/(?P<id>\w+)/$', ConfigletDetail.as_view(), name='detail_view'),
)
