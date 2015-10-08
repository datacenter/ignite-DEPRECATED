__author__  = "arunrajms"

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from views import PoolList
from views import PoolDetailList

urlpatterns = patterns('',
    url(r'^$',PoolList.as_view(),name='Full_Pools'),
    url(r'^(?P<id>\w+)/$',PoolDetailList.as_view(),name='Full_Pools'),
)
