#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django import template

register = template.Library()

@register.filter
def form_elapsed_time(value):
    min = value % 60
    hour = value / 60
    return '%d 時間 %d 分' % (hour,min)

@register.filter
def taglist(value):
    tags = []
    for tag in value.all():
        tags.append("<a href='/note/tag/%s/'>%s</a>" % (tag.name,tag.name))
    return ', '.join(tags)

@register.filter
def add_br(value):
    return value.replace('\n','<br />')
