
from django.urls import path
from . import views

app_name ="payinfo" # 应用命名空间

urlpatterns = [

    path('', views.payinfo,name='payinfo'),

]
