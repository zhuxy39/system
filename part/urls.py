"""MIS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    # 账户部分
    path('admin/', admin.site.urls),
    path('',views.MIS_login,name="MIS_login"),
    path("login/",views.login,name="login"),
    path('home/',views.home,name="home"),
    path("homepage/",views.homepage,name="homepage"),
    path("signup/", views.signup, name = "signup"),
    path("active/<str:active_code>/", views.active, name="active"),
    path("reset_password/", views.reset_password, name="reset_password"),
    path("confirm_reset/<str:active_code>/", views.confirm_reset, name="confirm_reset"),
    #用户管理和设备申请部分
    path('student-list/',views.student_list,name='student_list'),
    path('teacher-list/',views.teacher_list,name='teacher_list'),
    path('device-list/',views.device_list,name='device_list'),
    path('student_info/',views.student_info,name='student_info'),
    path('teacher_info/',views.teacher_info,name='teacher_info'),
    path('device_info/',views.device_info,name='device_info'),
    path('suspend/<str:netid>/',views.suspend,name='suspend'),
    path('recover/<str:netid>/',views.recover,name='recover'),
    path('delete/<str:netid>/',views.delete,name='delete'),
    path('modify/<str:netid>/',views.modify,name='modify'),
    path('add_device/',views.add_device,name="add_device"),
    path('delete_device/',views.delete_device,name="delete_device"),
    path('device_apply/',views.Device_apply,name='device_apply'),
    path('device_apply_info/',views.device_apply_info,name='device_apply_info'),
    path('detail/',views.detail,name='detail'),
    path('detail_info/<str:apply_id>/',views.detail_info,name='detail_info'),
    path('reject_apply/',views.reject_apply,name='reject_apply'),
    path('agree_apply/',views.agree_apply,name='agree_apply'),
    path('device_apply_record/',views.Device_apply_record,name='/device_apply_record/'),
    path('device_apply_record_info/',views.device_apply_record_info,name='device_apply_record_info'),
    path('device_broken/',views.Device_broken,name='device_broken'),
    path('device_broken_info/',views.device_broken_info,name='device_broken_info'),
    path('deal_broken/',views.deal_broken,name='deal_broken'),
    path('add_student/',views.add_student,name="add_student"),
    path('add_teacher/',views.add_teacher,name='add_teacher'),
    path('submit_device_apply/',views.submit_device_apply,name='submit_device_apply'),
    path('get_device_apply_info/',views.get_device_apply_info,name='get_device_apply_info'),
    path('submit/',views.submit,name='submit'),
    path('apply_detail/',views.apply_detail,name='apply_detail'),
    # 课室管理部分
    path('classroom-list/',views.classroom_list,name ='classroom_list'),
    path('classroom_info/',views.classroom_info,name ='classroom_info'),
    path('add_classroom/<str:classroom_id>/', views.add_classroom, name = 'add_classroom'),
    path('suspend_classroom/<str:classroom_id>/', views.suspend_classroom, name = 'suspend_classroom'),
    path('delete_classroom/<str:classroom_id>/', views.delete_classroom, name = 'delete_classroom'),
    path('active_classroom/<str:classroom_id>/', views.active_classroom, name = 'active_classroom'),
    path('modify_classroom/<str:classroom_id>/', views.modify_classroom, name = 'modify_classroom'),
    path('classroom_device/<str:classroom_id>/', views.classroom_device, name = 'classroom_device'),
    path('classroom_detail/<str:classroom_id>/', views.classroom_detail, name = 'classroom_detail'),
    path('classroom-apply-1/', views.classroom_apply_1, name = 'classroom_apply_1'),
    path('apply_classroom_list_1/', views.apply_classroom_list_1, name = 'apply_classroom_list_1'),
    path('pass_classroom_apply_1/<str:classroom_apply_id>/', views.pass_classroom_apply_1, name = 'pass_classroom_apply_1'),
    path('pass_classroom_apply_2/<str:classroom_apply_id>/', views.pass_classroom_apply_2, name = 'pass_classroom_apply_2'),
    path('refuse_classroom_apply/<str:classroom_apply_id>/', views.refuse_classroom_apply, name = 'refuse_classroom_apply'),
    path('classroom_apply_reason/<str:classroom_apply_id>/', views.classroom_apply_reason, name = 'classroom_apply_reason'),
    path('classroom-apply-2/', views.classroom_apply_2, name = 'classroom_apply_2'),
    path('apply_classroom_list_2/', views.apply_classroom_list_2, name = 'apply_classroom_list_2'),
    path('classroom-apply-record/', views.classroom_apply_record, name = 'classroom_apply_record'),
    path('apply_classroom_record/', views.apply_classroom_record, name = 'apply_classroom_record'),
    path('choose_available_classroom/<str:classroom_apply_id>/', views.choose_available_classroom, name = 'choose_available_classroom'),

]
