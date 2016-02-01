from django.conf.urls import patterns, include, url

from views import ProfileList, ProfileDetail
from views import FeatureList, FeatureDetail


urlpatterns = patterns('',
    url(r'^/feature/(?P<id>[1-9][0-9]*)$', FeatureDetail.as_view()),
    url(r'^/feature$', FeatureList.as_view()),
    url(r'^/profile/(?P<id>[1-9][0-9]*)$', ProfileDetail.as_view()),
    url(r'^/profile$', ProfileList.as_view()),
)
