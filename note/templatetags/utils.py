#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django import template
from django.conf import settings
import creole2html
import creole

register = template.Library()

@register.filter
def calc_totaltime(notes):
    return sum([note.elapsed_time for note in notes])

@register.filter
def convert_content(content, text_type):
    converted = ''
    NORMAL = 1
    WIKI = 2
    if text_type == NORMAL:
        converted = content.replace('\n', '<br />')
    elif text_type == WIKI:
        p = creole.Parser(content)
        converted = creole2html.HtmlEmitter(p.parse()).emit()
    return converted

@register.filter
def get_longtitle(content):
    return settings.LONG_TITLE

@register.filter
def get_shorttitle(content):
    return settings.SHORT_TITLE
