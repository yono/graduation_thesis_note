#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from datetime import datetime
from graduate.note.models import Note, Tag, Comment, User
from graduate.note.widgets import SplitSelectDateTimeWidget, ElapsedTimeWidget, SelectTimeWidget, TagWidget, TagField


class NoteForm(forms.ModelForm):

    user = forms.ModelChoiceField(queryset=User.objects.all(),
            widget=forms.HiddenInput())
    title = forms.CharField(label=u'タイトル', max_length=200)
    content = forms.CharField(label=u'内容',widget=forms.Textarea(attrs={'cols':'70', 'rows':'20'}))
    locate = forms.CharField(label=u'場所', max_length=100)
    date = forms.DateTimeField(label=u'日付', initial=datetime.now(), 
            widget=SelectDateWidget(years=range(2000, 2021)))
    start = forms.DateTimeField(label=u'開始時刻', initial=datetime.now(),
            widget=SplitSelectDateTimeWidget(minute_step=5, years=range(2000, 2021)))
    end = forms.DateTimeField(label=u'終了時刻', initial=datetime.now(),
            widget=SplitSelectDateTimeWidget(minute_step=5, years=range(2000,2021)))
    elapsed_time = forms.IntegerField(label='経過時間', 
            widget=ElapsedTimeWidget(attrs={'size':'5'}))
    tag = TagField(widget=TagWidget(attrs={'size':'30'}))
    text_type = forms.IntegerField(label='テキストタイプ', 
            widget=forms.Select(choices=(('1','HTML'),('2','Wiki'))))

    class Meta:
        model = Note

class CommentForm(forms.ModelForm):

    posted_date = forms.DateTimeField(initial=datetime.now(), 
            widget=forms.DateTimeInput(attrs={"readonly":"readonly"}))
    note = forms.ModelChoiceField(queryset=Note.objects.all(),
            widget=forms.HiddenInput())
    
    class Meta:
        model = Comment
