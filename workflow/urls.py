from django.conf.urls import patterns, url

from views import *

urlpatterns = patterns('',
    url(r'^/task/(?P<id>[1-9][0-9]*)$', TaskDetail.as_view()),
    url(r'^/task$', TaskList.as_view()),
    url(r'^/workflow/(?P<id>[1-9][0-9]*)$', WorkflowDetail.as_view()),
    url(r'^/workflow$', WorkflowList.as_view()),
)
