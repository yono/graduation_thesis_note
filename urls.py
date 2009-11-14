# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^graduate/', include('graduate.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^note/$','graduate.note.views.index'),
    # ユーザのノート一覧
    (r'^note/user/(?P<user_nick>\w+)/$','graduate.note.views.user'),
    # ユーザの年度別のノート一覧
    (r'^note/user/(?P<user_nick>\w+)/(?P<year>\d+)/$','graduate.note.views.user_year'),
    # ユーザの月ごとのノート一覧
    (r'^note/user/(?P<user_nick>\w+)/(?P<year>\d+)/(?P<month>\d+)/$','graduate.note.views.user_month'),
    # ユーザのノート詳細
    (r'^note/user/(?P<user_nick>\w+)/(?P<year>\d+)/(?P<month>\d+)/(?P<note_id>\d+)/$','graduate.note.views.note'),

    # ノート作成
    (r'^note/note_new/$','graduate.note.views.note_new'),
    (r'^note/note_create/$','graduate.note.views.note_create'),

    (r'^note/auth/login/$','graduate.note.views.mylogin'),

    # CSS
    (r'^site_media/(?P<path>.+)$','django.views.static.serve',{'document_root':'/Users/yono/hg/django/graduate/templates'}),
)
