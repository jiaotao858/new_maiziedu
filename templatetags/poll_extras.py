#!usr/bin/env python  
#-*- coding:utf-8 _*-  
""" 
@author:x1c 
@file: poll_extras.py 
@time: 2018/07/{DAY} 
@description:
"""

from django import template

register = template.Library()

@register.filter(name='cut')
def cut(value, arg):
    "Removes all values of arg from the given string"
    return value.replace(arg, '')