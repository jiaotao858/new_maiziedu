# !usr/bin/env python
# -*- coding:utf-8 _*-

""" 
@author:x1c 
@file: urls.py 
@time: 2018/05/{DAY} 
@description:
"""

from django.conf.urls import url
from maizi.common import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'common'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'showImg/', views.showImg, name='showImg'),
    url(r'search/', views.search_course, name='search'),
    url(r'login/', views.login_view, name='login'),
    url(r'logout/', views.logout_view, name='logout'),
    url(r'register/', views.register_view, name='register'),
    url(r'teacher/(?P<teacherid>[0-9]+)/$', views.teacher_view, name='teacher'),
    # url(r'change/', views.change_view, name='change'),
    url(r'course_player/(?P<courseid>[0-9]+)/$', views.course_player_view, name='course_player'),
    url(r'course_player/lesson/(?P<courseid>[0-9]+)/(?P<lessonid>[0-9]+)/$', views.course_player_view, name='course_player'),
    url(r'^discuss_post/$', views.discuss_post, name='discuss_post'),
    url(r'^course_list/$', views.course_list, name='course_list'),
    url(r'^course_stage/(?P<courseid>[0-9]+)$', views.course_stage, name='course_stage'),
    url(r'^home/teacher/info/(?P<userid>[0-9]+)$', views.personal_teacher_info, name='home_teacher_info'),
    url(r'^home/teacher/message/(?P<userid>[0-9]+)$', views.personal_teacher_message, name='home_teacher_message'),
    url(r'^home/teacher/class/(?P<userid>[0-9]+)$', views.personal_teacher_class, name='home_teacher_class'),
    url(r'^home/student/(?P<userid>[0-9]+)$', views.personal_student, name='home_student'),
    url(r'^home/teacher/info/change/', views.change_teacher_info, name='change_teacher_info'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)   # 指定映射文件路径

