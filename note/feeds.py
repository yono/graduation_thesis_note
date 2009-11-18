#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.contrib.syndication.feeds import Feed
from graduate.note.models import Note

class LatestNoteFeed(Feed):
    title = u"NAL研卒業研究ノート"
    link = "http://127.0.0.0:8000/note/"
    description = u"NAL研卒業研究ノート"

    def items(self):
        return Note.objects.order_by("-id")[:5]
