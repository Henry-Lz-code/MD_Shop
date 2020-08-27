from django.shortcuts import render
from django.http import HttpResponse
from django.views import View

# Create your views here.


class UserRegister(View):
    """用户注册视图"""

    def get(self, request):
        """
        返回注册页面

        :param request:
        :return:
        """
        return HttpResponse("获取注册页面")

    def post(self, request):
        """
        用户注册

        :param request:
        :return:
        """
        pass
