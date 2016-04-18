"""healthnet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from healthnet import views
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^dashboard/', views.dashboard, name="dashboard"),
    url(r'^log/', views.log, name="log"),
    url(r'^result/(?P<pk>\d+)/', views.result, name="result"),
    url(r'^prescription/(?P<pk>\d+)/', views.prescription, name="prescription"),
    url(r'^$', views.index, name="index"),
    url(r'^cancel_appointment/(?P<pk>\d+)/$', views.cancel_appointment, name="cancel_appointment"),
    url(r'^remove_prescription/(?P<pk>\d+)/$', views.remove_prescription, name="remove_prescription"),
    url(r'^register/', views.registration, name="registration"),
    url(r'^logout/', views.logout, name="logout"),
    url(r'^appointment/', views.appointment, name="appointment"),
    url(r'^edit_info/(?P<pk>\d+)/$', views.edit_info, name="edit_info"),
    url(r'^edit_info/', views.edit_info, name="edit_info"),
    url(r'^edit_appointment/(?P<pk>\d+)/', views.edit_appointment, name="edit_appointment"),
    url(r'^release_test_result/(?P<pk>\d+)/', views.release_test_result, name="release_test_result"),
    url(r'^create_test_result/(?P<pk>\d+)/', views.create_test_result, name="create_test_result"),
    url(r'^create_prescription/(?P<pk>\d+)/', views.create_prescription, name="create_prescription"),
    url(r'^toggle_admit/(?P<pk>\d+)/$', views.toggle_admit, name="toggle_admit"),
    url(r'^transfer/(?P<pk>\d+)/$', views.transfer, name="transfer"),
    url(r'^toggle_read/(?P<pk>\d+)/$', views.toggle_read, name="toggle_read"),
    url(r'^approve_user/(?P<pk>\d+)/$', views.approve_user, name="approve_user"),
    url(r'^send_message/(?P<pk>\d+)/$', views.send_message, name="send_message"),
    url(r'^send_message/', views.send_message, name="send_message"),
    url(r'^reply_message/(?P<pk>\d+)/$', views.reply_message, name="reply_message"),
    url(r'^sent_messages/', views.sent_messages, name="sent_messages"),
    url(r'^inbox/', views.inbox, name="inbox"),
    url(r'^doctor_registration/', views.doctor_registration, name="doctor_registration"),
    url(r'^nurse_registration/', views.nurse_registration, name="nurse_registration"),
    url(r'^admin_registration/', views.admin_registration, name="admin_registration"),





    # DEBUG
    url(r'^debug/create_test_user', views.create_test_user, name="create_test_user"),
    url(r'^debug/create_admin_user', views.create_admin_user, name="create_admin_user"),
    url(r'^debug/create_test_doctor', views.create_test_doctor, name="create_test_doctor"),
    url(r'^debug/create_test_nurse', views.create_test_nurse, name="create_test_nurse"),
]
