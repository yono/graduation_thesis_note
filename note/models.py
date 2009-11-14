from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import models as auth_models

## B4, M1, Teacher, etc..
class Group(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class MyUser(User):
    nick = models.CharField(max_length=100)
    belongs = models.ManyToManyField(Group, through='Belong')
    objects = auth_models.UserManager()

    def __unicode__(self):
        return self.nick

class Belong(models.Model):
    myuser = models.ForeignKey(MyUser)
    group = models.ForeignKey(Group)
    start = models.DateField()
    end = models.DateField(null=True,blank=True)

    def __unicode__(self):
        return '%s-%s' % (self.group.name,self.myuser.nick)

class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class Comment(models.Model):
    name = models.CharField(max_length=200)
    content = models.TextField()

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
    comment = models.ForeignKey(Comment)

    def __unicode__(self):
        return self.title


from django.contrib import admin
admin.site.register(MyUser)
admin.site.register(Note)
admin.site.register(Group)
admin.site.register(Belong)
