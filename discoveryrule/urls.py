__author__  = "arunrajms"

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt

from views import DiscoveryRuleList
from views import DiscoveryRuleDetailList


urlpatterns = patterns('',
    url(r'^$',DiscoveryRuleList.as_view(),name='Full_Pools'),
    url(r'^(?P<id>\w+)/$',DiscoveryRuleDetailList.as_view(),name='Full_Pools'),
)
