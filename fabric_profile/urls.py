
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from fabric_profile.views import FabricProfileList,FabricProfileDetail, ProfileTemplateList,ProfileTemplateDetail

urlpatterns = patterns('',
    # Examples:
     url(r'^$',FabricProfileList.as_view(), name='fabric_profile_home'),
     url(r'^(?P<id>\w+)$', FabricProfileDetail.as_view(), name='fabric_profile_detail_view'),
     url(r'^profile_template/$',ProfileTemplateList.as_view(), name='home'),
     url(r'^profile_template/(?P<id>\w+)$', ProfileTemplateDetail.as_view(), name='profiletemplate_detail_view'),
     
     )
