# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from graduate.note.feeds import LatestNoteFeed

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

feeds = {
    'latest': LatestNoteFeed,
}

urlpatterns = patterns('',
    # Example:
    # (r'^graduate/', include('graduate.foo.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^note/$','graduate.note.views.index'),
    # ユーザのノート一覧
    (r'^note/user/(?P<user_nick>\w+)/$','graduate.note.views.user'),
    # ユーザの年度別のノート一覧
    #(r'^note/user/(?P<user_nick>\w+)/(?P<year>\d+)/$','graduate.note.views.user_year'),

    # ユーザのノート詳細
    (r'^note/user/(?P<user_nick>\w+)/(?P<note_id>\d+)/$','graduate.note.views.note'),

    # ノート作成
    (r'^note/note_new/$','graduate.note.views.note_new'),
    (r'^note/note_create/$','graduate.note.views.note_create'),

    # ノート編集
    (r'^note/note_edit/(?P<note_id>\d+)/$','graduate.note.views.note_edit'),
    (r'^note/note_update/(?P<note_id>\d+)/$','graduate.note.views.note_update'),

    # mixiで言うところのホーム
    (r'^note/home/$','graduate.note.views.home'),

    # タグ
    (r'^note/tag/(?P<tag_name>\w+)/$','graduate.note.views.tag'),

    # ユーザ認証
    (r'^note/auth/login/$','django.contrib.auth.views.login',{'template_name':'note/login.html'}),
    (r'^note/auth/logout/$','django.contrib.auth.views.logout',{'template_name':'note/logout.html'}),


    #RSS
    (r'^note/rss/(?P<url>.*)/$','django.contrib.syndication.views.feed',{'feed_dict':feeds}),

    # CSS
    (r'^site_media/(?P<path>.+)$','django.views.static.serve',{'document_root':'/Users/yono/hg/django/graduate/templates'}),
)
