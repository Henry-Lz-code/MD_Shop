#!/usr/bin/env python3.6.5
# -*- coding: utf-8 -*-
# author:henry time:2020/8/28 17:45

from django.urls import path, re_path

from .views import CheckImageView, CheckMobileView


urlpatterns = [
    path("image_codes/<uuid:uuid>/", CheckImageView.as_view(), name="image_code"),
    re_path("sms_codes/(?P<mobile>1[3-9]\d{9})/", CheckMobileView.as_view(), name="send_sms")
]
