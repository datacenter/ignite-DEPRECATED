from django.conf.urls import patterns, url

from views import *

urlpatterns = patterns('',
    url(r'^/linecard/(?P<id>[1-9][0-9]*)$', LineCardDetailView.as_view()),
    url(r'^/linecard$', LineCardListView.as_view()),
    url(r'^/model/(?P<id>[1-9][0-9]*)$', SwitchDetailView.as_view()),
    url(r'^/model$', SwitchListView.as_view()),
)
