from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as _UserManger


class UserManger(_UserManger):
    """用户管理类"""
    def create_superuser(self, username, password, email=None, **extra_fields):
        """修改创建用户时所必须的email为None"""
        return super(UserManger, self).create_superuser(username=username, password=password,
                                                        email=email, **extra_fields)


class User(AbstractUser):
    """用户模型"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号", help_text="输入你的手机号",
                              error_messages={"unique": "mobile already exists", "max_length": "手机号不能超过20位"})

    email_active = models.BooleanField(default=False, verbose_name="邮箱是否活跃")

    objects = UserManger()
    REQUIRED_FIELDS = ['mobile']

    class Meta:
        db_table = "tb_user"
        verbose_name = "用户表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "<User {}>".format(self.username)
