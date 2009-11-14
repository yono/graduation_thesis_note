from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.auth import models as auth_models

class MyUser(User):
    belongs = models.ManyToManyField(Group, through='Belong')
    objects = auth_models.UserManager()

    def __unicode__(self):
        return self.username

    def fullname(self):
        return '%s%s' %  (self.last_name,self.first_name)

class Belong(models.Model):
    user = models.ForeignKey(MyUser)
    group = models.ForeignKey(Group)
    start = models.DateField()
    end = models.DateField(null=True,blank=True)

    def __unicode__(self):
        return '%s-%s' % (self.group.name,self.user.username)

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
    user = models.ForeignKey(MyUser)
    tag = models.ManyToManyField(Tag)

    def __unicode__(self):
        return self.title

class Comment(models.Model):
    name = models.CharField(max_length=200)
    content = models.TextField()
    note = models.ForeignKey(Note)

    def __unicode__(self):
        return self.name

from django.contrib import admin
admin.site.register(MyUser)
admin.site.register(Note)
admin.site.register(Belong)
admin.site.register(Tag)
