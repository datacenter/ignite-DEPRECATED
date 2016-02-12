from django.conf.urls import patterns, url

from views import *

urlpatterns = patterns('',
    url(r'^/group$', GroupList.as_view()),
    url(r'^/group/(?P<id>[1-9][0-9]*)$', GroupDetail.as_view()),
    url(r'^/group/(?P<gid>[1-9][0-9]*)/switch$', GroupSwitchList.as_view()),
    url(r'^/job$', JobList.as_view()),
    url(r'^/job/(?P<id>[1-9][0-9]*)$', JobDetail.as_view()),
)
