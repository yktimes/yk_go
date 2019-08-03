from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from shortuuidfield import ShortUUIDField
from django.db import models


class UserManager(BaseUserManager):

    # 创建 用户
    def _create_user(self,telephone,username,password,**kwargs):
        if not telephone:
            return ValueError("请输入手机号")
        if not username:
            return ValueError("请输入用户名")
        if not password:
            return ValueError("请输入密码")

        user = self.model(telephone=telephone,username=username,**kwargs)
        user.set_password(password)
        user.save() # 记得保存哦
        return user

    # 创建 普通用户
    def create_user(self,telephone,username,password,**kwargs):
        kwargs['is_superuser']=False
        return self._create_user(telephone,username,password,**kwargs)

    def create_superuser(self,telephone,username,password,**kwargs):
        kwargs['is_superuser'] =True
        return self._create_user(telephone, username, password, **kwargs)


class User(AbstractBaseUser,PermissionsMixin):
    # 我们不使用默认的自增长的主键
    # 用uuid shortuuid
    uid = ShortUUIDField(primary_key=True)
    telephone = models.CharField(max_length=11,unique=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    data_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD ='telephone'
    #
    REQUIRED_FIELDS = ['username']
    EMAIL_FIELD='email'

    objects = UserManager()


    def get_full_name(self):

        return self.username

    def get_short_name(self):
        return self.username