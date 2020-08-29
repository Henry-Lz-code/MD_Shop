#!/usr/bin/env python3.6.5
# -*- coding: utf-8 -*-
# author:henry time:2020/8/27 15:35

from django.utils.deprecation import MiddlewareMixin


class TestMiddle1(MiddlewareMixin):
    def __init__(self, get_response=None):
        print("初始化1中间件")
        super(TestMiddle1, self).__init__(get_response)

    def process_request(self, request):
        """处理请求前自动调用"""
        print('process_request1 被调用')

    def process_view(self, request, view_func, view_args, view_kwargs):
        # 处理视图前自动调用
        print('process_view1 被调用')

    def process_response(self, request, response):
        """在每个响应返回给客户端之前自动调用"""
        print('process_response1 被调用')
        return response


class TestMiddle2(MiddlewareMixin):
    def __init__(self, get_response=None):
        print("初始化2中间件")
        super(TestMiddle2, self).__init__(get_response)

    def process_request(self, request):
        """处理请求前自动调用"""
        print('process_request2 被调用')

    def process_view(self, request, view_func, view_args, view_kwargs):
        # 处理视图前自动调用
        print('process_view2 被调用')

    def process_response(self, request, response):
        """在每个响应返回给客户端之前自动调用"""
        print('process_response2 被调用')
        return response
