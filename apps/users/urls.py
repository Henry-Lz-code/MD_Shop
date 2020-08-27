#!/usr/bin/env python3.6.5
# -*- coding: utf-8 -*-
# author:henry time:2020/8/25 21:55

from django.urls import path
from .views import UserRegister


urlpatterns = [
    path("register/", UserRegister.as_view(), name="register"),
]
