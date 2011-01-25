#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.contrib.syndication.feeds import Feed
from graduate.note.models import Note,User,Comment
from django.conf import settings
from django.utils.feedgenerator import Atom1Feed
import datetime

url = settings.ABSOLUTE_URL
TITLE = settings.LONG_TITLE
class LatestNoteFeed(Feed):
    title = TITLE
    link = url
    description = TITLE

    def item_pubdate(self, obj):
        return obj.start

    def items(self):
        return Note.objects.order_by("-start")[:10]

class UserNoteFeed(Feed):

    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return User.objects.get(username=bits[0])

    def title(self, obj):
        return u"%s: %s%s のノート" % \
                (TITLE, obj.last_name,obj.first_name)

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def item_pubdate(self, obj):
        return obj.start

    def description(self, obj):
        return TITLE

    def items(self,obj):
        return Note.objects.filter(user=obj).order_by("-start")[:10]

class CommentFeed(Feed):
    title = u"%s: コメントRSS" % (TITLE)
    link = url
    description = TITLE

    def items(self):
        return Comment.objects.order_by("-posted_date")[:10]

    def item_pubdate(self, obj):
        return obj.posted_date
