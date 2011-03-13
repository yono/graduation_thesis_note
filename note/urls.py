# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.contrib.syndication.views import feed
from django.contrib.auth.views import login, logout
from graduate.note.feeds import LatestNoteFeed,UserNoteFeed,CommentFeed

feeds = {
    'latest': LatestNoteFeed,
    'user':UserNoteFeed,
    'comment':CommentFeed,
}

urlpatterns = patterns('graduate.note.views',

    # トップページ
    (r'^$','index'),

    # ユーザのノート一覧
    (r'^user/(?P<user_nick>\w+)/$','user'),

    # ユーザ情報
    (r'^user_info/(?P<user_nick>\w+)/$','user_info'),

    # ノート詳細
    (r'^note_detail/(?P<note_id>\d+)/$','note'),

    # ノート作成
    (r'^note_new/$','note_new'),
    (r'^note_create/$','note_create'),

    # ノート編集
    (r'^note_edit/$','note_edit'),
    (r'^note_update/$','note_update'),

    # ノート削除
    (r'^note_delete/$','note_delete'),
    (r'^note_destroy/$','note_destroy'),

    # コメント
    (r'^post_comment/$','post_comment'),

    # ユーザーごとのホーム
    (r'^home/$','home'),

    # タグ一覧
    (r'^tag/$','tag'),

    # ユーザ認証
    (r'^auth/login/$',login,{'template_name':'note/login.html'}),
    (r'^auth/logout/$',logout,{'template_name':'note/logout.html'}),

    #RSS
    (r'^rss/(?P<url>.*)/$',feed,{'feed_dict':feeds}),

    #検索
    (r'^search/$','search'),

    #合計時間のJSON
    (r'^json/(?P<user_nick>\w+)$', 'time_json'),
)
