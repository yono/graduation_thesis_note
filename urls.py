# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
import config

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^note/', include('graduate.note.urls')),

    # CSS
    (r'^site_media/(?P<path>.+)$','django.views.static.serve',
        {'document_root':config.get_option('django','template_dir')}),
)
