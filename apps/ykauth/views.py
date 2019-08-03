from django.contrib.auth import login,logout,authenticate
from django.views.decorators.http import require_POST
from .forms import LoginForm
from django.http import JsonResponse
from utils import restful

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

        return restful.params_error(message=errors)

