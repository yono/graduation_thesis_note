#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django import template

register = template.Library()

@register.filter
def calc_totaltime(notes):
    return sum([note.elapsed_time for note in notes])
