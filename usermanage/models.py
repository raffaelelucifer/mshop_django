#_*_ coding: utf-8 _*_
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
import datetime

class UserManage(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=200)
    #telephone = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=0)

    def __str__(self):
        return self.name
    
#class UserActive(models.Model):
#    name = models.CharField(max_length=100)
#    email = models.CharField(max_length=200)
#    #email_title = models.CharField(max_length=200)
#    #email_body = models.CharField(max_length=500)
#    is_active = models.BooleanField(default=0)
#
#    def __str__(self):
#        return self.name
