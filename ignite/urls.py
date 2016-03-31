from django.conf.urls import patterns, include, url
from django.contrib import admin

from . import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ignite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    # Auth URL
    url(r'^auth/', include('djoser.urls')),

    # Swagger URL
    url(r'^docs/', include('rest_framework_swagger.urls')),

    # UI URL
    url(r'^ui/(?P<path>.*)$', 'django.views.static.serve',
        { 'document_root': settings.UI_ROOT, }),

    # Ignite URLs
    url(r'^api/admin', include('administration.urls')),
    url(r'^/*api/bootstrap', include('bootstrap.urls')),
    url(r'^api/config', include('config.urls')),
    url(r'^api/discovery', include('discovery.urls')),
    url(r'^api/fabric', include('fabric.urls')),
    url(r'^api/feature', include('feature.urls')),
    url(r'^api/manage', include('group.urls')),
    url(r'^api/image', include('image.urls')),
    url(r'^api/pool', include('pool.urls')),
    url(r'^api/switch', include('switch.urls')),
    url(r'^api/workflow', include('workflow.urls')),
)
