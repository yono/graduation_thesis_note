# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User as AuthUser, Group
from django.contrib.auth import models as auth_models
from django.conf import settings
from django.db import connection

url = settings.ABSOLUTE_URL

class Grade(models.Model):
    name = models.CharField(max_length=100)
    formalname = models.CharField(max_length=100)
    priority = models.IntegerField(max_length=100)

    def __unicode__(self):
        return self.name

class User(AuthUser):
    belongs = models.ManyToManyField(Grade, through='Belong')
    objects = auth_models.UserManager()

    def __unicode__(self):
        return self.username

    def fullname(self):
        return u'%s%s' %  (self.last_name,self.first_name)

    def get_absolute_url(self):
        return "%suser/%s/" % (url,self.username)

class Belong(models.Model):
    user = models.ForeignKey(User)
    grade = models.ForeignKey(Grade)
    start = models.DateField()
    end = models.DateField(null=True,blank=True)

    def __unicode__(self):
        return '%s-%s' % (self.grade.name,self.user.username)

class Tag(models.Model):
    name = models.CharField(max_length=255,unique=True)

    def __unicode__(self):
        return self.name

class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    locate = models.CharField(max_length=100)
    date = models.DateField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    elapsed_time = models.IntegerField()
    user = models.ForeignKey(User)
    tag = models.ManyToManyField(Tag)
    text_type = models.IntegerField()
    has_metadata = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title

    def taglist(self):
        tags = []
        for tag in self.tag.all():
            tags.append(tag.name)
        return ', '.join(tags)

    def get_absolute_url(self):
        return "%snote_detail/%d/" % (url,self.id)

class Comment(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()
    note = models.ForeignKey(Note)
    posted_date = models.DateTimeField()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "%snote_detail/%d/" % (url,self.note.id)

class Word(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=300)
    idf = models.FloatField(null=True, blank=True)
    freq = models.IntegerField(null=True, blank=True)
    df = models.IntegerField(null=True, blank=True)
    appear_ratio = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = u'word'

class Metadata(models.Model):
    id = models.IntegerField(primary_key=True)
    weight = models.FloatField()
    note = models.ForeignKey(Note)
    word = models.ForeignKey(Word,related_name='words')
    org = models.ForeignKey(Word,related_name='orgs')
    class Meta:
        db_table = u'metadata'

class NoteDate(object):
    def __init__(self, year, month):
        self.year = year
        self.month = month

class NoteList(object):
    
    notes = []
    
    def __init__(self, notes=[]):
        self.notes = notes
        self.dates = []
    
    def sort_by_date(self):

        dates = dict([((note.date.year, note.date.month),0) for note in self.notes])
        dates = dates.keys()
        dates.sort(self._compare_by_year_month, reverse=True)
        self.dates = [NoteDate(date[0], date[1]) for date in dates]

    def _compare_by_year_month(self, x, y):
        if cmp(x[0], y[0]) != 0:
            return cmp(x[0], y[0])
        else:
            return cmp(x[1], y[1])

class TagCloudNode(object):
    def __init__(self, tag, cssclass):
        self.tag = tag
        self.cssclass = cssclass

class TagCloud(object):

    css_classes = ['nube'+str(i) for i in xrange(1, 6)]
    nodes = []

    def __init__(self, notes=[]):

        tags = {}

        # タグの出現回数を数える
        if len(notes) == 0:
            cursor = connection.cursor()
            cursor.execute('''
            SELECT
                t.name, 
                count(tg.id) 
            FROM 
                note_tag t,
                note_note_tag tg
            WHERE
                t.id = tg.tag_id
            GROUP BY
                tg.tag_id
            ''')
            tags = dict(cursor.fetchall())

        for note in notes:
            for tag in note.tag.all():
                tags[tag.name] = tags.get(tag.name, 0) + 1

        # タグの出現回数に応じてフォントの大きさを決定 
        fontmax = -1000
        fontmin = 1000
        for tag_num  in tags.values():
            fontmax = max(fontmax, tag_num)
            fontmin = min(fontmin, tag_num)

        print self.css_classes
        divisor = ((fontmax - fontmin) / len(self.css_classes)) + 1

        self.nodes = [TagCloudNode(t, self.css_classes[(n - fontmin)/divisor]) for t, n in tags.items()]
    

from django.contrib import admin
admin.site.register(Note)
admin.site.register(Belong)
admin.site.register(Tag)
admin.site.register(Grade)
