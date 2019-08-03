from django.urls import path,include
from apps.news import views

urlpatterns = [
    path('', views.index,name="index"),

    path('cms/', include("apps.cms.urls")),
    path('account/', include("apps.ykauth.urls")),

    path('news/', include("apps.news.urls")),
    path('course/', include("apps.course.urls")),
    path('payinfo/', include("apps.payinfo.urls")),

]
