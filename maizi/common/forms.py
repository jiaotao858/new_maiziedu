# !usr/bin/env python
# -*- coding:utf-8 _*-

""" 
@author:x1c 
@file: forms.py 
@time: 2018/06/{DAY} 
@description:
"""
from django import forms


# 用户登陆表单
class UserForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(max_length=50)


# 创建用户表单
class RegForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(max_length=50)
    email = forms.EmailField(max_length=30)


# 修改教师信息表单
class TeaInfoForm(forms.Form):
    username = forms.CharField(max_length=30)
    position = forms.CharField(max_length=30)
    description = forms.CharField(max_length=200,required=False)
    qq = forms.IntegerField()
    mobile = forms.IntegerField()
    email = forms.EmailField(max_length=200)


