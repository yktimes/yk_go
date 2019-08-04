from django import forms
from apps.forms import FormMixin
from .models import User
from django_redis import get_redis_connection
import re
from utils import restful

class LoginForm(forms.Form,FormMixin):
    telephone= forms.CharField(max_length=11)
    password = forms.CharField(max_length=20,min_length=6,error_messages={
        "max_length":"密码最多不能超过20个字符",
        "min_length":"密码不能少于6个字符"
    })
    remember = forms.IntegerField(required=False)


class RegisterForm(forms.Form,FormMixin):
    telephone = forms.CharField(max_length=11)
    username = forms.CharField(max_length=20)
    password1 = forms.CharField(max_length=20, min_length=6, error_messages={
        "max_length": "密码最多不能超过20个字符",
        "min_length": "密码不能少于6个字符"
    })
    password2 = forms.CharField(max_length=20, min_length=6, error_messages={
        "max_length": "密码最多不能超过20个字符",
        "min_length": "密码不能少于6个字符"
    })
    img_captcha = forms.CharField(min_length=4, max_length=4,error_messages={
        "max_length": "只允许4个字符",
        "min_length": "只允许4个字符"
    })
    sms_captcha = forms.CharField(min_length=6, max_length=6,error_messages={
        "max_length": "只允许6个数字",
        "min_length": "只允许6个数字"
    })


    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        username = cleaned_data.get('username')
        telephone = cleaned_data.get('telephone')
        img_captcha = cleaned_data.get('img_captcha')
        sms_captcha = cleaned_data.get('sms_captcha')

        if not all([username,password2,password1,telephone,img_captcha,sms_captcha]):
            raise forms.ValidationError("参数不允许为空")


        if not re.match(r'^1[3-9]\d{9}$', telephone):

            raise forms.ValidationError('手机号格式错误')

        if password1 != password2:
            raise forms.ValidationError('两次密码输入不一致！')




        redis_conn = get_redis_connection('img_captcha')
        cached_img_captcha = redis_conn.get(img_captcha.lower())
        print("1111",cached_img_captcha)
        print(111,cached_img_captcha)
        if not cached_img_captcha or cached_img_captcha.decode().lower() != img_captcha.lower():
            raise forms.ValidationError("图形验证码错误！")

        exists = User.objects.filter(telephone=telephone).exists()
        if exists:
            raise forms.ValidationError('该手机号码已经被注册！')


        # 判断短信验证码
        redis_conn = get_redis_connection('verify_codes')

        real_sms_code = redis_conn.get('sms_%s' % telephone)
        if real_sms_code is None:
            raise forms.ValidationError('无效的短信验证码')
        if sms_captcha != real_sms_code.decode():
            raise forms.ValidationError('短信验证码错误')

        return cleaned_data







