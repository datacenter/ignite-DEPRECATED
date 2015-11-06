__author__  = "arunrajms"

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt

from views import DiscoveryRuleList, DiscoveryRuleDetailList, DeployedByGlobal


urlpatterns = patterns('',
    url(r'^$',DiscoveryRuleList.as_view(),name='Full_Pools'),
    url(r'^$',DiscoveryRuleList.as_view(),name='home_view'),
    url(r'^deployed/$',DeployedByGlobal.as_view()),
    url(r'^(?P<id>[1-9][0-9]*)/$',DiscoveryRuleDetailList.as_view(),name='Detail_View'),
)
