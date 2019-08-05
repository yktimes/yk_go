from django.urls import path,include
from apps.news import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('', views.index,name="index"),

    path('cms/', include("apps.cms.urls")),
    path('account/', include("apps.ykauth.urls")),

    path('news/', include("apps.news.urls")),
    path('course/', include("apps.course.urls")),
    path('payinfo/', include("apps.payinfo.urls")),
    path('ueditor/',include('apps.ueditor.urls'))

]+static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
