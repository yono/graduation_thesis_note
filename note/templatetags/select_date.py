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
