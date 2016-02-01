from django.conf.urls import patterns, include, url

from views import DiscoveryRuleList, DiscoveryRuleDetailList


urlpatterns = patterns('',
    url(r'^/rule$', DiscoveryRuleList.as_view()),
    url(r'^/rule/(?P<id>[1-9][0-9]*)/$', DiscoveryRuleDetailList.as_view()),
)
