#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.contrib.syndication.feeds import Feed
from graduate.note.models import Note,User

class LatestNoteFeed(Feed):
    title = u"NAL研卒業研究ノート"
    link = "http://127.0.0.0:8000/note/"
    description = u"NAL研卒業研究ノート"

    def items(self):
        return Note.objects.order_by("-id")[:5]

class UserNoteFeed(Feed):

    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return User.objects.get(username=bits[0])

    def title(self, obj):
        return u"NAL研卒業研究ノート: %s%s のノート" % (obj.last_name,obj.first_name)

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return u"NAL研究卒業研究ノート"

    def items(self,obj):
        return Note.objects.filter(user=obj).order_by("-id")[:5]
