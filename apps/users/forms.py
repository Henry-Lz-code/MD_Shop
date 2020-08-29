#!/usr/bin/env python3.6.5
# -*- coding: utf-8 -*-
# author:henry time:2020/8/27 20:33

import logging
from django import forms
from django.contrib.auth import login
from django.core.validators import RegexValidator, ValidationError
from django_redis import get_redis_connection

from users.models import User
from users.constants import USER_SESSION_EXPIRY_TIME


logger = logging.getLogger("django")


username_validator = RegexValidator(regex=r"^[0-9a-zA-Z_-]{5,20}$", message="用户名格式错误")
mobile_validator = RegexValidator(r'^1[3-9]\d{9}$', message="手机号格式错误")
sms_validator = RegexValidator(r'^\d{6}$', message="短信验证码错误")


class RegisterForm(forms.Form):
    """注册校验表单"""
    user_name = forms.CharField(label="用户名", max_length=20, min_length=5, validators=[username_validator],
                                help_text="请输入用户名", error_messages={"require": "用户名不能为空",
                                                                    "min_length": "用户名长度不能小于5",
                                                                    "max_length": "用户名长度不能超过20"})
    pwd = forms.CharField(label="密码", max_length=20, min_length=8, help_text="请输入密码",
                          error_messages={"require": "密码不能为空",
                                          "min_length": "密码长度不能低于8个字符",
                                          "max_length": "密码长度不能超过20个字符"})
    cpwd = forms.CharField(label="确认密码", max_length=20, min_length=8, help_text="请再次输入密码",
                           error_messages={"require": "密码不能为空",
                                           "min_length": "密码长度不能低于8个字符",
                                           "max_length": "密码长度不能超过20个字符"})
    phone = forms.CharField(label="手机号码", max_length=11, min_length=11, validators=[mobile_validator],
                            help_text="请输入手机号", error_messages={"require": "手机号不能为空",
                                                                "max_length": "手机号格式错误",
                                                                "min_length": "手机号格式错误"})
    msg_code = forms.CharField(label="短信验证码", max_length=6, min_length=6, validators=[],
                               help_text="请输入短信验证码", error_messages={"require": "短信验证码不能为空",
                                                                     "max_length": "短信验证码错误",
                                                                     "min_length": "短信验证码错误"})

    def clean_user_name(self):
        """校验用户名"""
        username = self.cleaned_data.get("user_name")
        if User.objects.filter(username=username).exists():
            raise ValidationError("该用户名已注册")
        return username

    def clean_phone(self):
        """校验手机号码"""
        mobile = self.cleaned_data.get("phone")
        if User.objects.filter(mobile=mobile).exists():
            raise ValidationError("该手机号已注册")
        return mobile

    def clean(self):
        """校验两次输入的密码和短信验证码"""
        cleaned_data = super().clean()
        password = cleaned_data.get("pwd")
        confirm_password = cleaned_data.get("cpwd")
        mobile = cleaned_data.get("phone")
        sms_code = cleaned_data.get("msg_code")

        # 校验两次输入的密码是否一致
        if password != confirm_password:
            raise ValidationError("两次输入的密码不一样")

        # 校验短信验证码
        try:
            conn = get_redis_connection(alias="verify_codes")
            key = "sms_code_{}".format(mobile)
            send_code = conn.get(key)
        except Exception as e:
            logger.error("连接redis数据库失败:{}".format(e))
            raise ValidationError("服务端错误")
        else:
            real_sms_code = send_code.decode("utf-8") if send_code else None
            if (not real_sms_code) or (real_sms_code != sms_code):
                raise ValidationError("短信验证码错误")


class LoginForm(forms.Form):
    """登录校验表单"""
    username = forms.CharField(label="用户名", max_length=20, min_length=5, validators=[username_validator],
                               help_text="请输入用户名", error_messages={"require": "用户名不能为空",
                                                                   "min_length": "用户名长度不能小于5",
                                                                   "max_length": "用户名长度不能超过20"})
    pwd = forms.CharField(label="密码", max_length=20, min_length=8, help_text="请输入密码",
                               error_messages={"require": "密码不能为空",
                                               "min_length": "密码长度不能低于8个字符",
                                               "max_length": "密码长度不能超过20个字符"})
    remembered = forms.CharField(label="记住登录密码", required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        """登录校验"""
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("pwd")
        remembered = cleaned_data.get("remembered")

        user = User.objects.get(username=username)
        if not user:
            raise ValidationError("用户名不存在")
        if user.check_password(password):
            if remembered:
                self.request.session.set_expiry(USER_SESSION_EXPIRY_TIME)
            else:
                self.request.session.set_expiry(0)
            login(self.request, user)
        else:
            raise ValidationError("密码错误")
