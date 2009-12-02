#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django import forms
from django.contrib import admin
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext, ugettext_lazy as _
from models import User

class UserAddForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username","first_name","last_name")
    def __init__(self, *args, **kwards):
        return super(UserAddForm,self).__init__( *args, **kwards)

class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
    password = forms.CharField( help_text=_("Use '[algo]$[salt]$[hexdigest]' or use the <a href=\"password/\">change password form</a>."))

class UserAdmin(AuthUserAdmin):
    form = UserAdminForm
    add_form = UserAddForm
    model = User

admin.site.register(User, UserAdmin)
