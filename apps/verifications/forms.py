#!/usr/bin/env python3.6.5
# -*- coding: utf-8 -*-
# author:henry time:2020/8/28 21:28

import logging

from django import forms
from django.core.validators import RegexValidator, ValidationError
from django_redis import get_redis_connection

from users.models import User

mobile_validator = RegexValidator(r'^1[3-9]\d{9}$', message="手机号格式错误")
image_code_validator = RegexValidator(r'^[a-zA-Z0-9]{4}$', message="图形验证码错误")

logger = logging.getLogger("django")


class CheckMobileForm(forms.Form):
    """校验手机号表单"""
    mobile = forms.CharField(label="手机号码", max_length=11, min_length=11, validators=[mobile_validator],
                             help_text="请输入手机号", error_messages={"require": "手机号不能为空",
                                                                 "max_length": "手机号格式错误",
                                                                 "min_length": "手机号格式错误"})
    image_code = forms.CharField(label="图形验证码", max_length=4, min_length=4, validators=[image_code_validator],
                                 help_text="请输入手机号", error_messages={"require": "图形验证码不能为空",
                                                                     "max_length": "图形验证码错误",
                                                                     "min_length": "图形验证码错误"})
    image_code_id = forms.UUIDField(label="uuid", help_text="UUID", error_messages={"require": "图形验证码不能为空"})

    def clean(self):
        """发送短信验证码"""
        cleaned_data = super().clean()
        image_code = cleaned_data.get("image_code")
        image_code_id = cleaned_data.get("image_code_id")
        mobile = cleaned_data.get("mobile")
        # 校验手机号是否已注册
        if User.objects.filter(mobile=mobile).exists():
            raise ValidationError("该手机号已注册")
        # 校验图形验证码
        try:
            conn = get_redis_connection(alias="verify_codes")
            redis_image_code = conn.get("img-{}".format(image_code_id))
        except Exception as e:
            logger.error("连接数据库失败: {}".format(e))
            raise ValidationError("未知错误")
        real_image_code = redis_image_code.decode("utf-8") if redis_image_code else None
        if (not real_image_code) or (image_code.upper() != real_image_code):
            raise ValidationError("图形验证码错误")

        mobile_flag = "sms_flag_{}".format(mobile)
        flag = conn.get(mobile_flag)
        if flag:
            raise ValidationError("验证码已发送")
