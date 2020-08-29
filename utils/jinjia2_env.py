from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse


def jinjia2_env(**options):
    """配置jinjia2环境变量"""
    env = Environment(**options)
    # 将static和url语法配置到变量中
    env.globals.update({
        "static": staticfiles_storage.url,
        "url": reverse
    })
    return env

