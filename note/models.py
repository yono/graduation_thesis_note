from django.db import models
from django.contrib.auth.models import User as AuthUser, Group
from django.contrib.auth import models as auth_models


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
        return "http://127.0.0.1:8000/note/user/%s/" % (self.username)

class Belong(models.Model):
    user = models.ForeignKey(User)
    grade = models.ForeignKey(Grade)
    start = models.DateField()
    end = models.DateField(null=True,blank=True)

    def __unicode__(self):
        return '%s-%s' % (self.grade.name,self.user.username)

class Tag(models.Model):
    name = models.CharField(max_length=100,unique=True)

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

    def __unicode__(self):
        return self.title

    def taglist(self):
        tags = []
        for tag in self.tag.all():
            tags.append(tag.name)
        return ', '.join(tags)

    def get_absolute_url(self):
        return "http://127.0.0.1:8000/note/user/%s/%d" % (self.user.username,self.id)

class Comment(models.Model):
    name = models.CharField(max_length=200)
    content = models.TextField()
    note = models.ForeignKey(Note)
    posted_date = models.DateTimeField()

    def __unicode__(self):
        return self.name

from django.contrib import admin
admin.site.register(Note)
admin.site.register(Belong)
admin.site.register(Tag)
admin.site.register(Grade)
