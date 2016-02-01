from django.conf.urls import patterns, url

from views import *

urlpatterns = patterns('',
    url(r'^/aaa/server$', AAAServerListView.as_view()),
    url(r'^/aaa/server/(?P<id>[1-9][0-9]*)$', AAAServerDetailView.as_view()),

    url(r'^/aaa/user$', AAAUserListView.as_view()),
    url(r'^/aaa/user/(?P<id>[1-9][0-9]*)$', AAAUserDetailView.as_view()),

    url(r'^/backup$', IgniteBackupView.as_view()),
    url(r'^/backup/(?P<fn>\d\d\d\d_\d\d_\d\d_\d*)$', IgniteBackupDetailView.as_view()),
)
