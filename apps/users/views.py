from django.contrib.auth import login, logout
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views import View

from users.forms import RegisterForm, LoginForm
from users.models import User


class VerifyUserNameView(View):
    """校验用户名视图"""

    def get(self, request, username):
        """校验用户名是否重名"""
        count = User.objects.filter(username=username).count()
        return JsonResponse({"count": count})


class VerifyPhoneView(View):
    """校验手机号视图"""

    def get(self, request, mobile):
        """校验手机号是否重复"""
        count = User.objects.filter(mobile=mobile).count()
        return JsonResponse({"count": count})


class RegisterView(View):
    """用户注册视图"""

    def get(self, request):
        """
        返回注册页面
        """
        return render(request, "register.html")

    def post(self, request):
        """
        用户注册逻辑实现
        """
        form_data = request.POST
        form = RegisterForm(data=form_data)
        if form.is_valid():
            username = form.cleaned_data.get("user_name")
            password = form.cleaned_data.get("pwd")
            mobile = form.cleaned_data.get("phone")
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
            login(request, user)
            return HttpResponse("跳转到首页")
        else:
            errmsg_list = []
            for item in form.errors.get_json_data().values():
                errmsg_list.append(item[0].get("message"))
            errmsg = ",".join(errmsg_list)
            return HttpResponse(content=errmsg, status=402)


class LoginView(View):
    """用户登录视图"""

    def get(self, request):
        """
        登录页面
        """
        return render(request, "login.html", {"loginerror": ""})

    def post(self, request):
        """用户登录实现"""
        form = LoginForm(data=request.POST, request=request)
        if form.is_valid():
            return HttpResponse("首页面")
        else:
            error_list = []
            for item in form.errors.get_json_data().values():
                error_list.append(item[0].get("message"))
            errmsg = ",".join(error_list)
            return JsonResponse({"errmsg": errmsg})


class LogoutView(View):
    """用户登出视图"""

    def get(self, request):
        """登出用户"""
        logout(request)
        return HttpResponse("首页面")
