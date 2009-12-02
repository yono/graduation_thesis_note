# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^note/', include('graduate.note.urls')),

    # CSSなど
    (r'^site_media/(?P<path>.+)$','django.views.static.serve',
        {'document_root':os.path.join(BASE_DIR,'templates')}),
)
