#_*_ encoding: utf-8 *_*
from django import forms
from django.forms import ModelForm
from mysite import models

class OrderForm(forms.ModelForm):
    class Meta:
        model = models.Order
        fields = ['full_name', 'address', 'phone']
 
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['full_name'].label = '收件人姓名'
        self.fields['address'].label = '邮件地址'
        self.fields['phone'].label = '联系电话'

