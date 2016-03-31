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
    url(r'^/rma/rma$',
        RmaSerialUpdateView.as_view()),
    url(r'^/rma/(?P<id>[0-9A-Za-z]+)$',
        RmaSerialSearchView.as_view()),
    url(r'^/downloads/config/(?P<id>[1-9][0-9]*).cfg$',
        BootstrapDownloadConfigView.as_view()),
    url(r'^/downloads/yaml/(?P<id>[1-9][0-9]*).yml$',
        YamlView.as_view()),
    url(r'^/downloads/scripts/(?P<script_name>[\w.]{1,256})$',
        BootstrapScriptView.as_view()),
    url(r'^/downloads/packages/(?P<pkg_name>.+\.(tar.gz))$',
        BootstrapPackageView.as_view()),
)
