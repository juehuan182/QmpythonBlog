"""QmpythonBlog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
#from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve

from rest_framework import routers, serializers, viewsets

from .views import index, column, category, tag, Article
from user.models import Account


# Seriallzers 定义这个API的表现
class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    class Meta:
        model = Article  # 指明序列化器处理数据字段从模型类参考生成
        fields = ['title', 'description', 'cover_img', 'read_num', 'like_num', 'author'] # 指明该序列化器包含的模型类中有哪些字段,’all’指明包含所有字段


#ViewSets定义这个API的行为
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()   # queryset 指明该视图在查询数据时使用的查询集
    serializer_class = ArticleSerializer  # serializer_class 指明该视图在进行序列化或反序列化时使用的序列化器

#Routers提供了一种简单的方式来设置url
router = routers.DefaultRouter()
router.register(r'articles', ArticleViewSet)

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('admin/', include('admin.urls', namespace='admin')),

    path('api/', include(router.urls)),
    # 通过username/password获取token
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # 注意这个url可以是任何你想要的，但是必须导入 rest_framework.urls，并且 namespace必须为rest_framework。
    # 在django1.9+中，你可以不用设置namespace,rest_framework将会为你设置。

    path('', index, name='index'),

    #栏目
    path('columns/<int:column_id>/', column, name='columns'),

    # 文章分类
    path('categories/<int:category_id>/', category, name='categories'),

    # 文章标签
    path('tag/<int:tag_id>/', tag, name='tag'),

    # 文章
    path('articles/', include('article.urls', namespace='articles')),

    # 用户
    #url(r'^user/', include('user.urls', namespace='account')), # 1.x版本使用url
    #re_path(r'^user/', include('user.urls', namespace='account')), # 等同于之前的url使用方法，可以使用正则匹配url
    path('user/', include('user.urls', namespace='user')),  # 2.x使用namespace需要在对应app-urls下注册app_name

    # 文档
    path('docs/', include('doc.urls', namespace='docs')),

    # 验证
    path('verification/', include('verification.urls', namespace='verification')),


] #+ static(MEDIA_URL, document_root=MEDIA_ROOT)   #方法2；在最后通过static方法，把MEDIA_URL加进去，这样模板中才能正确显示图片。因为图片属于静态文件。

if settings.DEBUG:
    urlpatterns += [re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),]
else:
    urlpatterns += [re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}, name='static'),]

# 网站地图
from django.contrib.sitemaps.views import sitemap
from util.sitemaps import ArticleSitemap, TagSitemap, CategorySitemap

sitemaps = {
    'articles': ArticleSitemap,
    'tags': TagSitemap,
    'categories': CategorySitemap
}

urlpatterns += [re_path(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),]

#from django.contrib.sitemaps import GenericSitemap
#from article.views import Article
#sitemap框架提供了一个快捷类GenericSitemap，快速生成网站地图，无需为sitemap编写单独的视图模块，直接在URLCONF中，
# 获取对象，获取参数，传递参数，设置url
# sitemaps = {
#     'blog': GenericSitemap({'queryset': Article.objects.all(), 'date_field': 'create_time'}, priority=1.0),
#     # 如果还要加其它的可以模仿上面的
# }


# 添加robots协议

from django.views.generic import TemplateView

urlpatterns += [re_path(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots'),]

