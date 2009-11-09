from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import models as auth_models

## B4, M1, Teacher, etc..
class Group(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class MyUser(User):
    belong = models.ManyToManyField(Group)

    def __unicode__(self):
        return self.username

class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    locate = models.CharField(max_length=100)
    date = models.DateTimeField()
    user = models.ForeignKey(MyUser)

    def __unicode__(self):
        return self.title
