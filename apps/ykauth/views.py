from django.contrib.auth import login,logout,authenticate
from django.views.decorators.http import require_POST
from .forms import LoginForm,RegisterForm
from django.http import JsonResponse
from utils import restful
from django.shortcuts import redirect,reverse
from utils.captcha.ykzcaptcha import Captcha
from io import BytesIO
from django.http.response import HttpResponse

from django_redis import get_redis_connection
from utils.aliyunsdk import aliyunsms
import re
from . import constants
from django.contrib.auth import get_user_model
import random


User = get_user_model()

@require_POST
def login_view(request):
    form = LoginForm(request.POST)
    if form.is_valid():
        telephone = form.cleaned_data.get("telephone")
        password = form.cleaned_data.get("password")
        remember = form.cleaned_data.get("remember")

        user = authenticate(request,username=telephone,password=password)

        if user:
            if user.is_active: # 正常用户
                login(request,user)
                if remember:
                    request.session.set_expiry(None) # 默认使用2个星期
                else:
                    request.session.set_expiry(0) # 退出浏览器清除session

                return restful.ok()

            else: # 说明该用户是黑名单用户

                return restful.unauth(message="您的账号被冻结，请联系管理员")
        else:
            return restful.params_error(message="账号或密码错误")

    else:
        errors =  form.get_errors()
        print("login",errors)
        return restful.params_error(message=errors)


def logout_view(request):
    logout(request)
    return redirect(reverse("index"))

@require_POST
def register(request):
    form = RegisterForm(request.POST)
    if form.is_valid():
        telephone = form.cleaned_data.get('telephone')
        username=form.cleaned_data.get('username')
        password = form.cleaned_data.get('password2')
        user = User.objects.create_user(
            telephone=telephone,
            username=username,
            password=password
        )
        print(user)
        login(request,user)

        return restful.ok()

    else:
        print(form.get_errors())
        return restful.params_error(message=form.get_errors())



def img_captcha(request):
    text,image = Captcha.gene_code()
    # BytesIO：相当于一个管道，用来存储图片的流数据
    out = BytesIO()
    # 调用image的save方法，将这个image对象保存到BytesIO中
    image.save(out,'png')
    # 将BytesIO的文件指针移动到最开始的位置
    out.seek(0)

    response = HttpResponse(content_type='image/png')
    # 从BytesIO的管道中，读取出图片数据，保存到response对象上
    response.write(out.read())
    response['Content-length'] = out.tell()

    # 12Df：12Df.lower()
    redis_conn = get_redis_connection('img_captcha')
    redis_conn.setex(text.lower(), constants.SMS_CODE_REDIS_EXPIRES,text.lower())


    return response



def sms_captcha(request):
    telephone = request.GET.get("telephone")



    # ret =  re.match(r"^1[35678]\d{9}$", telephone)

    if telephone:

        # 保存短信验证码与发送记录
        redis_conn = get_redis_connection('verify_codes')
        # 判断图片验证码, 判断是否在60s内
        send_flag = redis_conn.get("send_flag_%s" % telephone)
        if send_flag:
            return restful.params_error(message="请求次数过于频繁")

        # 生成短信验证码
        sms_code = "%06d" % random.randint(0, 999999)

        pl = redis_conn.pipeline()
        pl.setex("sms_%s" % telephone, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("send_flag_%s" % telephone, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()

        try:

                result = aliyunsms.send_sms(telephone,sms_code)
                print(result)

                return restful.ok()


        except Exception as e:
            return restful.params_error(message="网络错误")

    else:
        return restful.params_error(message="请填写正确的手机号码")