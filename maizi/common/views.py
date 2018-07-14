# !usr/bin/env python
# -*- coding:utf-8 _*-

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User,Group
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from maizi.common.forms import UserForm, RegForm,TeaInfoForm
from .models import Ad, Keywords, Course, CareerCourse, Links, RecommendKeywords, RecommendedReading, UserProfile, \
    Lesson, Discuss, LessonResource, CourseResource, Stage
import json


# 全局变量（需要注册到setting中）
def global_setting(request):
    # 广告数据
    ad_list = Ad.objects.all()
    # 友情链接数据
    link_list = Links.objects.all()
    # 推荐搜索标签
    keyword_list = RecommendKeywords.objects.all()

    # 首页推荐文章（官方活动）
    article_av = RecommendedReading.objects.filter(reading_type=RecommendedReading.ACTIVITY)
    # 首页推荐文章（开发者资讯）
    article_nw = RecommendedReading.objects.filter(reading_type=RecommendedReading.NEWS)
    # 首页推荐文章（技术交流）
    article_dc = RecommendedReading.objects.filter(reading_type=RecommendedReading.DISCUSS)

    # 最新上传课程
    new_course_list = Course.objects.all().order_by('date_publish')
    # 最多播放课程
    play_count_list = Course.objects.all().order_by('click_count')
    # 最具体人气课程
    favorite_count_list = Course.objects.all().order_by('favorite_count')

    # 老师和学生列表（通过扩展用户组获取）
    teacher_list = UserProfile.objects.filter(groups__name='teacher')
    user_list = UserProfile.objects.filter(groups__name='student')
    return locals()


# 用户用户相关内容
def get_context_data(request, **kwargs):
    if request.user.is_authenticated():
        current_user_set = request.user
        print(current_user_set)
        current_group_set = Group.objects.get(user=current_user_set)
        print(current_group_set)
        print(type(current_group_set))
    return locals()


# 首页
# @login_required
def index(request):
    return render(request, "common/index.html", locals())


# 登陆(@csrf_exempt允许跨域)
@csrf_exempt
def login_view(request):
    context = {}
    if request.method == 'POST':
        login_form = UserForm(request.POST)
        # is_valid()验证字段格式是都正确，cleaned_data数据清洗，变成一个python接受得数据类型
        if login_form.is_valid():
            # 获取email用户密码
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            # 获取的表单数据与数据库进行比较，认证给出的用户名和密码
            user = authenticate(username=username, password=password)
            if user is not None:
                # 比较成功，跳转index
                user.backend = 'django.contrib.auth.backends.ModelBackend'  # 指定默认的登录验证方式
                login(request, user)
            else:
                return render(request,'common/failure.html',{'reason':'登陆失败'})
            return redirect(request.POST.get('source_url'))
        # else:
        #     # 比较失败，还在login
        #     # context = {'isLogin': False, 'pawd': False}
        return render(request, 'common/failure.html', {'reason':login_form.errors})
    # else:
    #     context = {'isLogin': False, 'pswd': True}
    return render(request, 'common/login.html', locals())


# 注销登陆(重定向至首页)
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


# 注册视图
@csrf_exempt
def register_view(request):

        if request.method == 'POST':
            username = request.POST.get('username', '')
            email = request.POST.get('email', '')
            password = request.POST.get('password', '')
            password1 = request.POST.get('password1', '')
            errors = []
            reg_form = RegForm({'username': username, 'password': password, 'password1': password1,'email':email})

            # 判断格式是否正确
            if not reg_form.is_valid():
                return render(request, "common/failure.html", {'reason': reg_form.errors})
            # 判断两次密码是否一致
            elif password != password1:
                errors.append("两次输入的密码不一致!")
                return render(request, "common/failure.html", {'reason':errors})
            # 判断用户名是否可用
            elif UserProfile.objects.filter(username=username):
                errors.append("用户名已存在")
                return render(request, "common/failure.html", {'reason':errors})
            else:
                new_user = UserProfile.objects.create(username=username, email=email, password=password)
                new_user.save()

            new_user.backend = 'django.contrib.auth.backends.ModelBackend'  # 指定默认的登录验证方式
            login(request, new_user)
            return redirect(request.POST.get('source_url'))
        else:
            reg_form = RegForm()
        return render(request, 'common/register.html', locals())


# 上传图片
# def uploadImg(request):
#     if request.method == 'POST':
#         img = Img(image_url=request.FILES.get('img'))
#         img.svae()
#     return render(request, 'imgupload.html')


# 图片显示
def showImg(request):
    "测试一下是否有图片显示"
    imgs = Ad.objects.all()
    context = {
        'imgs': imgs
    }
    return render(request, 'common/index.html', context=context)


# 老师视图
def teacher_view(request, teacherid):
    teacher = UserProfile.objects.filter(groups__name='teacher').get(id=teacherid)
    courses = Course.objects.filter(teacher=teacherid)
    return render(request, 'common/teacher.html', locals())


# 课程播放
@csrf_exempt
def course_player_view(request, courseid, lessonid=None, ):
    course = Course.objects.get(id=courseid)    # 课程
    lesson_list = Lesson.objects.filter(course=course.id)   # 视频章节
    teacher = UserProfile.objects.get(id=course.teacher.id)     # 授课老师
    resource_list = LessonResource.objects.filter(lesson=lessonid)  # 课程资源
    if lessonid is not None:
        curr_lesson_id = lessonid
        curr_lesson = Lesson.objects.get(id=lessonid)
        discusses = Discuss.objects.filter(lesson_id=lessonid).order_by('-id')
    else:   # 如果没有视频id，默认查询第一个视频相关信息
        curr_lesson_id = lesson_list[0].id
        curr_lesson = lesson_list[0]
        discusses = Discuss.objects.filter(lesson_id=lesson_list[0]).order_by('id')

    discuss_list = check_sub_discuss(discusses)
    return render(request, 'common/course_player.html', locals())


# 搜索视图【完成了一半】
def search_course(request):
    date = dict()
    keyword = request.GET.get("search", None)
    if keyword is not None:
        career_course = CareerCourse.objects.filter(name__icontains=keyword).order_by("index")
        course = Course.objects.filter(name__icontains=keyword).order_by("index")
    else:
        career_course = CareerCourse.objects.all().order_by("index")
        course = Course.objects.all().order_by("index")
    date["career_course"] = []
    for i in career_course:
        date["career_course"].append({'name': i.name, 'id': i.id})
    date["course"] = []
    for i in course:
        date["course"].append({'name': i.name, 'id': i.id})
    return HttpResponse(json.dumps(date))


# 区分析主评论和子评论
def check_sub_discuss(comments):
    comment_list = []
    for comment in comments:
        # 如果没有父评论，则为主评论，样式为：[父评论，父评论，父评论]
        if comment.parent_id is None:
            comment_list.append(comment)

        # 在父评论中增加一个'children_discuss'属性，属性默认的值为空集合
        for item in comment_list:
            if not hasattr(item,'children_discuss'):
                setattr(item,'children_discuss', [])
            # 查找父评论下子评论，放入对应子评论集合中
            if comment.parent_id == item:
                item.children_discuss.append(comment)
                break

    # 统计子评论数量
    for citem in comment_list:
        if len(citem.children_discuss) == 0:
            citem.discuss_num = ''
        else:
            citem.discuss_num = len(citem.children_discuss)

    return comment_list


# 提交评论
def discuss_post(request):
    if request.method == 'POST':
        user = UserProfile.objects.get(id=request.POST.get('user_id'))
        content = request.POST.get('content')
        lesson = request.POST.get('lesson_id')
        print(user)
        print(content)
        print(lesson)

        if request.POST.get('parent_id') is not None:
            discuss_p = Discuss.objects.get(id=request.POST.get('parent_id'))
        else:
            discuss_p = None
        discuss = Discuss(content=request.POST.get('content'),
                          parent_id=discuss_p,
                          lesson_id=request.POST.get('lesson_id'),
                          user_id=request.POST.get('user_id'))
        discuss.save()
        return redirect(request.META['HTTP_REFERER'])
    else:
        pass


# 课程列表
def course_list(request):
    courses = CareerCourse.objects.all()
    return render(request, "common/career_course_list.html", locals())


# 课程阶段
def course_stage(request, courseid):
    career = CareerCourse.objects.get(id=courseid)      # 职业课程
    stages = Stage.objects.filter(career_course=career.id)      # 职业课程阶段
    return render(request, "common/course_stage.html", locals())


# 个人中心-老师-个人资料
def personal_teacher_info(request, userid):
    userinfo = UserProfile.objects.get(id=userid)
    return render(request, "common/personalcenter_te_info.html", locals())


# 个人中心-老师-消息
def personal_teacher_message(request, userid):
    return render(request, "common/personalcenter_te_message.html", locals())


# 个人中心-老师-班级
def personal_teacher_class(request, userid):
    return render(request, "common/personalcenter_te_class.html", locals())


# 个人中心-学生-个人资料
def personal_student(request, userid):
    return render(request, "common/personalcenter_st_info.html", locals())

# 修改用户资料表单
# @csrf_exempt
# def change_view(request):
#     if request.method == 'POST':
#         form = ChaForm(request.POST)
#         if form.is_valid():
#             # 获得表单数据
#             username = form.cleaned_data['username']
#             position = form.cleaned_data['position']
#             description = form.cleaned_data['description']
#             qq = form.cleaned_data['qq']
#             # 添加到数据库（还可以加一些字段的处理）
#             user = UserProfile.objects.create(username=username, position=position,description=description,qq=qq)
#             user.save()
#             # 重定向之修改页
#             return redirect(request.META['HTTP_REFERER'])
#     else:
#         context = {'isLogin': False}
#     # 将req 、页面 、以及context{}（要传入html文件中的内容包含在字典里）返回
#     return render(request, 'common/teacher.html', locals())


# 修改教师信息
def change_teacher_info(request):
    if request.method == 'POST':
        teainfoform = TeaInfoForm(request.POST)
        if teainfoform.is_valid():
            username = teainfoform.cleaned_data['username']
            position = teainfoform.cleaned_data['username']
            qq = teainfoform.cleaned_data['username']
            mobile = teainfoform.cleaned_data['username']
            email = teainfoform.cleaned_data['username']
            # username = teainfoform.cleaned_data['username']
            # username = teainfoform.cleaned_data['username']
            # username = teainfoform.cleaned_data['username']
            teacher_info = UserProfile.objects.create(username=username,position=position,qq=qq,mobile=mobile,email=email)
            teacher_info.save()
            return redirect(request.POST.get('source_url'))
    else:
        teainfoform = TeaInfoForm()
    return render(request, 'common/personalcenter_te_info.html', {'teainfoform': teainfoform})