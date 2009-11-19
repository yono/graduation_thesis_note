# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from graduate.note.feeds import LatestNoteFeed,UserNoteFeed,CommentFeed

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

feeds = {
    'latest': LatestNoteFeed,
    'user':UserNoteFeed,
    'comment':CommentFeed,
}

urlpatterns = patterns('',
    # Example:
    # (r'^graduate/', include('graduate.foo.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^note/$','graduate.note.views.index'),
    # ユーザのノート一覧
    (r'^note/user/(?P<user_nick>\w+)/$','graduate.note.views.user'),

    # ユーザ情報
    (r'^note/user_info/(?P<user_nick>\w+)/$','graduate.note.views.user_info'),

    # ノート詳細
    (r'^note/user/(?P<user_nick>\w+)/(?P<note_id>\d+)/$','graduate.note.views.note'),

    # ノート作成
    (r'^note/note_new/$','graduate.note.views.note_new'),
    (r'^note/note_create/$','graduate.note.views.note_create'),

    # ノート編集
    (r'^note/note_edit/$','graduate.note.views.note_edit'),
    (r'^note/note_update/$','graduate.note.views.note_update'),
    # ノート削除
    (r'^note/note_delete/$','graduate.note.views.note_delete'),
    (r'^note/note_destroy/$','graduate.note.views.note_destroy'),

    # コメント
    (r'^note/post_comment/$','graduate.note.views.post_comment'),

    # mixiで言うところのホーム
    (r'^note/home/$','graduate.note.views.home'),

    # タグ一覧
    (r'^note/tag/$','graduate.note.views.tag'),

    # タグ
    (r'^note/tag/(?P<tag_name>\w+)/$','graduate.note.views.tag_detail'),

    # ユーザ認証
    (r'^note/auth/login/$','django.contrib.auth.views.login',{'template_name':'note/login.html'}),
    (r'^note/auth/logout/$','django.contrib.auth.views.logout',{'template_name':'note/logout.html'}),

    #RSS
    (r'^note/rss/(?P<url>.*)/$','django.contrib.syndication.views.feed',{'feed_dict':feeds}),

    #検索
    (r'^note/search/$','graduate.note.views.search'),

    # CSS
    (r'^site_media/(?P<path>.+)$','django.views.static.serve',{'document_root':'/Users/yono/hg/django/graduate/templates'}),
)
