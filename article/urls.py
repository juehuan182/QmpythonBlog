from django.urls import path

from .views import article_list, ArticleDetailView, ArticleCommentView, article_likes, ArticleSearchView


#我们通过 app_name='article' 告诉 Django 这个 urls.py 模块是属于article应用的，这种技术叫做视图函数命名空间。
#因为此处通过 name 属性给这些视图函数取了个别名，但是一个项目中可能也存在其他name叫同名的，为了防止冲突呢，方法就是通过 app_name 来指定命名空间

app_name = 'article'
urlpatterns = [

    # 文章列表
    path('', article_list, name='article_list'),

    # 文章详情（内容）
    path(r'detail-<int:article_id>.html', ArticleDetailView.as_view(), name='article_detail'),

    # 文章点赞
    path(r'<int:article_id>/likes/', article_likes, name='article_likes'),

    # 文章评论
    path(r'<int:article_id>/comments/', ArticleCommentView.as_view(), name='article_comments'),

    # 文章搜索
    path('search/', ArticleSearchView(), name='search'), #因为我们SearchView 默认是有__call__方法的，所以可以直接通过类名调用

]
