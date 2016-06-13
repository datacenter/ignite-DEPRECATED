from django.conf.urls import patterns, url

from views import *

urlpatterns = patterns('',
    url(r'^/group$', GroupList.as_view()),
    url(r'^/group/(?P<fab_id>[1-9][0-9]*)$', GroupListPerFabric.as_view()),
    url(r'^/group/(?P<fab_id>[1-9][0-9]*)/(?P<grp_id>[1-9][0-9]*)$', GroupDetail.as_view()),
    url(r'^/job$', JobList.as_view()),
    url(r'^/job/(?P<id>[1-9][0-9]*)$', JobDetail.as_view()),
    url(r'^/job/(?P<id>[1-9][0-9]*)/clone$', JobCloneView.as_view()),
    url(r'^/scriptlist$', ScriptList.as_view()),
)
