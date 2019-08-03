
from django.urls import path
from . import views

app_name ="news" # 应用命名空间

urlpatterns = [

    path('<int:news_id>/', views.news_detail,name='news_detail'),
    path('search/', views.search,name='search'),
]
