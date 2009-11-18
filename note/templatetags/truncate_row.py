#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django import template

register = template.Library()

@register.filter
def truncate_row(value):
    rows = value.splitlines()
    result = rows
    if len(rows) > 10:
        result = rows[:10]
        result.append(u'<br />.....（省略されました）<br />')
    return '\n'.join(result)
