__author__  = "arunrajms"

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from views import CollectionList
from views import CollectionDetailList

urlpatterns = patterns('',
    url(r'^$',CollectionList.as_view(),name='Full_Collections'),
    url(r'^(?P<id>\w+)/$',CollectionDetailList.as_view(),name='Full_Collections'),
)
