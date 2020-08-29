#!/usr/bin/env python3.6.5
# -*- coding: utf-8 -*-
# author:henry time:2020/8/25 21:55

from django.urls import path, re_path
from .views import RegisterView, LoginView, VerifyUserNameView, VerifyPhoneView

app_name = 'users'


urlpatterns = [
    re_path("usernames/(?P<username>\w{5,20})/count/", VerifyUserNameView.as_view(), name="username_count"),
    re_path("mobiles/(?P<mobile>1[3-9]\d{9})/count/", VerifyPhoneView.as_view(), name="mobile_count"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
]
