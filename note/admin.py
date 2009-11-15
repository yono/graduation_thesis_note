#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
#from django.contrib.auth import forms
from django.utils.translation import ugettext, ugettext_lazy as _
from models import MyUser

class MyUserAddForm(UserCreationForm):
    class Meta:
        model = MyUser
        fields = ("username","first_name","last_name")
    def __init__(self, *args, **kwards):
        return super(MyUserAddForm,self).__init__( *args, **kwards)

class MyUserAdminForm(forms.ModelForm):
    class Meta:
        model = MyUser
    password = forms.CharField( help_text=_("Use '[algo]$[salt]$[hexdigest]' or use the <a href=\"password/\">change password form</a>."))

class MyUserAdmin(UserAdmin):
    form = MyUserAdminForm
    add_form = MyUserAddForm
    model = MyUser

admin.site.register(MyUser, MyUserAdmin)
admin.site.unregister(User)
