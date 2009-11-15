#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django import template

register = template.Library()

@register.filter
def select_date(value):
    return value[0]

@register.filter
def is_selected(value):
    html = ''
    if value[1]:
        html = 'selected="selected"'
    return html

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
