__author__  = "Rohit N Dubey"

from django.conf.urls import patterns, include, url
from django.contrib import admin

from views import POAP

from . import prod

urlpatterns = patterns('',

    url(r'^ui/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': prod.UI_ROOT, }),

    url(r'^api/collection/', include('collection.urls')),
    url(r'^api/discoveryrule/', include('discoveryrule.urls')),
    url(r'^api/configuration/', include('configuration.urls')),
  #  url(r'^api/usermanagement/', include('usermanagement.urls')),
    url(r'^api/fabric/', include('fabric.urls')),
    url(r'^api/resource/', include('resource.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^auth/', include('djoser.urls')),
    url(r'^api/poap/', POAP.as_view(), name='home'),
)
