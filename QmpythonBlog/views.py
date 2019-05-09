import logging

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.core.cache import cache

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from article.models import Column, Category, Tag, Article, Advertising

# 导入日志器
logger = logging.getLogger('qmpython')

# from django.views.decorators.cache import cache_page
# @cache_page(60)
# 单个view视图缓存，如果视图中有其他不一样，比如有些数据，因不同人不一样，则用单个视图的方式不行，因为都缓存了
# 可以用底层操作cache，如以下set，get方式
# def index(request):
#     # 尝试从缓存中获取数据，如果没有返回None，那么从数据库查询存放到cache中
#     context = cache.get('index_page_data')
#     if context is None:
#         # print('设置缓存') #测试是否生效
#         # 获取文章
#         articles = Article.objects.only('id', 'cover_img', 'category', 'title', 'author', 'create_time',
#                                         'read_num', 'like_num').order_by('-create_time')  # 逆序排列
#         # 最新发布
#         new_articles = articles[0:settings.ONE_PAGE_COUNT]
#         # 轮播图
#         Advertisings = Advertising.objects.only('id').filter(is_delete=False)
#         leftAdvertisings = Advertisings.filter(position='top_left')
#         rightAdvertisings = Advertisings.filter(position='top_right')
#
#         # 获取首页标题，META关键词，META描述
#         import configparser
#         import os
#         config = configparser.ConfigParser()
#         conf_path = os.path.join(settings.BASE_DIR, 'util', 'web_info.ini')
#         config.read(conf_path, encoding='utf-8')
#         section_node = config.sections()[0]
#         web_title = config.get(section_node, "WEB_SITE_TITLE")
#         web_keywords = config.get(section_node, "WEB_SITE_KEYWORDS")
#         web_desc = config.get(section_node, "WEB_SITE_DESC")
#
#         context = {'new_articles': new_articles,
#                    'leftAdvertisings': leftAdvertisings,
#                    'rightAdvertisings': rightAdvertisings,
#                    'web_title': web_title,
#                    'web_keywords': web_keywords,
#                    'web_desc': web_desc
#                    }
#
#         # 设置缓存
#         # key value timeout
#         cache.set('index_page_data', context, 1)
#
#     # 如果有千人千面数据出现，则可以通过字典的update更新数据
#     #context.update('people': people)
#
#     return render(request, 'index.html', context=context)


def index(request):
    # print('设置缓存') #测试是否生效
    # 获取文章
    articles = Article.objects.only('id', 'cover_img', 'category', 'title', 'author', 'create_time',
                                    'read_num', 'like_num').order_by('-create_time')  # 逆序排列
    # 最新发布
    new_articles = articles[0:settings.ONE_PAGE_COUNT]
    # 轮播图
    Advertisings = Advertising.objects.only('id').filter(is_delete=False)
    leftAdvertisings = Advertisings.filter(position='top_left')
    rightAdvertisings = Advertisings.filter(position='top_right')

    # 获取首页标题，META关键词，META描述
    import configparser
    import os
    config = configparser.ConfigParser()
    conf_path = os.path.join(settings.BASE_DIR, 'util', 'web_info.ini')
    config.read(conf_path, encoding='utf-8')
    section_node = config.sections()[0]
    web_title = config.get(section_node, "WEB_SITE_TITLE")
    web_keywords = config.get(section_node, "WEB_SITE_KEYWORDS")
    web_desc = config.get(section_node, "WEB_SITE_DESC")

    context = {'new_articles': new_articles,
               'leftAdvertisings': leftAdvertisings,
               'rightAdvertisings': rightAdvertisings,
               'web_title': web_title,
               'web_keywords': web_keywords,
               'web_desc': web_desc
               }

    return render(request, 'index.html', context=context)



def column(request, column_id):
        column = get_object_or_404(Column, pk=column_id)
        # categories = column.category_set.all()
        categories = Category.objects.filter(column=column)

        return render(request, 'article/column.html', {'categories': categories})


def category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    # 主表去查字表，通过反向查询
    articles = category.article_set.all().only('cover_img', 'title', 'title', 'description',
                                               'author__username', 'create_time', 'read_num', 'like_num')
    # 分页数据
    try:
        page = int(request.GET.get('page', 1))  # 获取页码
    except PageNotAnInteger:
        logger.error("当前页数错误:PageNotAnInteger")
        page = 1

    # 实例化分页对象，articles需要分页的对象，在中间传一个数字，表示每页显示多少个
    paginator = Paginator(articles, settings.ONE_PAGE_COUNT, request=request)
    try:
        articles_info = paginator.page(page) #获取当前页的数据
    except EmptyPage:
        # 若访问的页数大于实际页数，则返回最后一页数据
        logger.info("访问的页数大于总页数")
        articles_info = paginator.page(paginator.num_pages)

    context = {'category': category, 'articles_info': articles_info}

    return render(request, 'article/category.html', context=context)


def tag(request, tag_id):
    # 通过标签查询文章，多对多的查询
    tag = get_object_or_404(Tag, pk=tag_id)
    articles = tag.article_set.all()

    # 分页数据
    try:
        page = request.GET.get('page', 1)  # 获取页码
    except PageNotAnInteger:
        page = 1

    # 实例化分页对象，articles需要分页的对象，在中间传一个数字，表示每页显示多少个
    paginator = Paginator(articles, settings.ONE_PAGE_COUNT, request=request)
    articles = paginator.page(page)  # 获取当前页的数据

    # print(article)
    context= {'tag': tag, 'article': articles, 'page': page}

    return render(request, 'article/tag.html', context=context)