from django.conf.urls import patterns, url

from views import *

urlpatterns = patterns('',
    url(r'^/config/(?P<id>[1-9][0-9]*)$',
        BootstrapConfigView.as_view()),
    url(r'^/logs/(?P<id>[1-9][0-9]*)$',
        BootstrapLogView.as_view()),
    url(r'^$',
        BootstrapView.as_view()),
    url(r'^/status$',
        BootstrapSwitchStatusView.as_view()),
    url(r'^/booted$',
        BootstrapBootedSwitchView.as_view()),
)
