from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import View
from django.views.decorators.http import require_POST,require_GET
from apps.news.models import NewsCategory,News
from utils import restful
from django.conf import settings
from .forms import EditNewsCategoryForm,WriteNewsForm

import os
import qiniu
# Create your views here.
@staff_member_required(login_url='index')
def index(request):

    return render(request,"cms/index.html")


class WriteNewView(View):

    def get(self,request):
        categories = NewsCategory.objects.all()

        context = {
            'categories':categories
        }

        return render(request,'cms/write_news.html',context=context)



    def post(self,request):
        form = WriteNewsForm(data=request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            desc = form.cleaned_data['desc']
            thumbnail = form.cleaned_data['thumbnail']
            content = form.cleaned_data['content']


            category_id = form.cleaned_data['category']
            category = NewsCategory.objects.get(pk=category_id)

            News.objects.create(title=title,content=content,category=category,desc=desc,
                                thumbnail=thumbnail,author=request.user
                                )

            return restful.ok()

        else:
            return restful.params_error(message=form.get_errors())




@require_GET
def news_category(request):
    category = NewsCategory.objects.all()
    return render(request,'cms/news_category.html',{'categories':category})

@require_POST
def add_news_category(request):
    name = request.POST.get('name')

    if not name.strip():
        return restful.params_error(message='名字不能为空')
    exists = NewsCategory.objects.filter(name=name).exists()
    if not exists:
        NewsCategory.objects.create(name=name)
        return restful.ok()

    else:
        return restful.params_error(message='该分类已存在')


@require_POST
def edit_news_category(request):
    form = EditNewsCategoryForm(request.POST)
    if form.is_valid():
        pk = form.cleaned_data.get('pk')
        name = form.cleaned_data.get('name')
        try:
            NewsCategory.objects.filter(pk=pk).update(name=name)
            return restful.ok()
        except:
            return restful.params_error(message='该分类不存在！')
    else:
        return restful.params_error(message=form.get_error())


@require_POST
def delete_news_category(request):
    pk = request.POST.get('pk')
    try:
        NewsCategory.objects.filter(pk=pk).delete()
        return restful.ok()
    except:
        return restful.unauth(message='该分类不存在！')







@require_POST
def upload_file(request):
    file = request.FILES.get('file')
    name = file.name

    with open(os.path.join(settings.MEDIA_ROOT, name), 'wb') as fp:
        for chunk in file.chunks():
            fp.write(chunk)
    url = request.build_absolute_uri(settings.MEDIA_URL + name)
    # http://127.0.1:8000/media/abc.jpg
    return restful.result(data={'url': url})



@require_GET
def qntoken(request):
    access_key = settings.QINIU_ACCESS_KEY
    secret_key = settings.QINIU_SECRET_KEY

    bucket = settings.QINIU_BUCKET_NAME
    q = qiniu.Auth(access_key,secret_key)

    token = q.upload_token(bucket)

    return restful.result(data={"token":token})