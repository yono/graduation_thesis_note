from django.db import models
from django.contrib.auth.models import User as AuthUser, Group
from django.contrib.auth import models as auth_models

url = 'http://www.nal.ie.u-ryukyu.ac.jp/note'

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
        return "%s/user/%s/" % (url,self.username)

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
        return "%s/user/%s/%d" % (url,self.user.username,self.id)

class Comment(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()
    note = models.ForeignKey(Note)
    posted_date = models.DateTimeField()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "%s/%s/%d" % (url,self.note.user.username,self.note.id)

from django.contrib import admin
admin.site.register(Note)
admin.site.register(Belong)
admin.site.register(Tag)
admin.site.register(Grade)
