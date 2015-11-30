from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import ImageProfileList, ImageProfileListDetail

urlpatterns = patterns('',
    # Examples:
     url(r'^$', ImageProfileList.as_view()),
     url(r'^(?P<id>[1-9][0-9]*)$', ImageProfileListDetail.as_view(), name='detail_view'),
)

