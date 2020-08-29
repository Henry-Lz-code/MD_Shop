import logging
import random

from django.views import View
from django.http import HttpResponse, HttpResponseServerError, JsonResponse
from django_redis import get_redis_connection

from .forms import CheckMobileForm
from libs.captcha.captcha import captcha
from utils.yuntongxun.sms import CCP
from .expire_time import IMAGE_CODE_REDIS_EXPIRE_TIME, SMS_CODE_REDIS_TIME, SEND_SMS_CODE_MARK, SMS_CODE_TEMP_ID

logger = logging.getLogger("django")


class CheckImageView(View):
    """图形验证码视图"""

    def get(self, request, uuid):
        """获取图片验证码"""
        _, image_code, image = captcha.generate_captcha()
        try:
            conn = get_redis_connection(alias="verify_codes")
        except Exception as e:
            logger.error("数据库链接失败: {}".format(e))
            return HttpResponseServerError("未知错误")
        else:
            conn.setex("img-{}".format(uuid), IMAGE_CODE_REDIS_EXPIRE_TIME, image_code)
        logger.info("image_code: {}".format(image_code))
        return HttpResponse(image, content_type="image/png")


class CheckMobileView(View):
    """校验手机号"""

    def get(self, request, mobile):
        """发生短信验证码"""
        image_code = request.GET.get("image_code")
        image_code_id = request.GET.get("image_code_id")

        data = {"mobile": mobile,
                "image_code": image_code,
                "image_code_id": image_code_id}
        form = CheckMobileForm(data=data)
        if form.is_valid():
            # 发送短信验证码
            sms_code = "%06d" % random.randint(0, 999999)
            try:
                conn = get_redis_connection(alias="verify_codes")
            except Exception as e:
                logger.error("redis连接失败: {}".format(e))
                return JsonResponse({"code": 4002, "errmsg": "发送短信异常"}, status=500)
            p = conn.pipeline()
            sms_flag_key = "sms_flag_{}".format(mobile)
            sms_code_key = "sms_code_{}".format(mobile)
            try:
                p.setex(sms_code_key, SMS_CODE_REDIS_TIME, sms_code)
                p.setex(sms_flag_key, SEND_SMS_CODE_MARK, 1)
                p.execute()
            except Exception as e:
                logger.error("redis执行失败: {}".format(e))
                return JsonResponse({"code": 4002, "errmsg": "发送短信异常"}, status=500)
            logger.info('sms code: {}'.format(sms_code))
            # 发送验证码
            try:
                result = CCP().send_template_sms(mobile, [sms_code, 5], SMS_CODE_TEMP_ID)
            except Exception as e:
                logger.error("短信验证码发送异常: [mobile: %s, message: %s]" % (mobile, e), status=500)
                return JsonResponse({"code": 4002, "errmsg": "发送短信异常"})
            else:
                if result == 0:
                    logger.info("短信验证码发送成功: [mobile: %s, message: %s]" % (mobile, sms_code))
                    return JsonResponse({"code": 0, "errmsg": "短信验证码发送成功"})
                else:
                    logger.info("发送短信验证码失败: [mobile: %s]" % mobile)
                    return JsonResponse({"code": 4002, "errmsg": "发送短信失败"}, status=500)
        else:
            errmsg_list = []
            print(form.errors.get_json_data())
            for item in form.errors.get_json_data().values():
                errmsg_list.append(item[0].get("message"))
            errmsg = ",".join(errmsg_list)
            return JsonResponse({"code": 4002, "errmsg": errmsg}, status=402)
