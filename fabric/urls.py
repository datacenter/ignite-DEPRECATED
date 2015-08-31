from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import TopologyList, TopologyDetail, FabricList, FabricDetail, FabricRuleDBDetail

urlpatterns = patterns('',
    # Examples:
     url(r'^$', FabricList.as_view(), name='home'),
     url(r'^(?P<id>[0-9]+)$', FabricDetail.as_view(), name='detail_view'),
     url(r'^fabricruledb/$', FabricRuleDBDetail.as_view(), name='detail_view'),
     url(r'^topology/$', TopologyList.as_view(), name='home'),
     url(r'^topology/(?P<id>[0-9]+)$', TopologyDetail.as_view(), name='detail_view'),
)
