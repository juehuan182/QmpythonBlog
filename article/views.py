import logging

from django.shortcuts import render, get_object_or_404
from django.views import View
from django.db.models import Count
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.conf import settings
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from .models import Article, Comment, ArticleLikeDetail, CommentNotification

from haystack.views import SearchView

logger = logging.getLogger('django')
def article_list(request):
    try:
        page = int(request.GET.get('page', 1))  #默认第一页
    except Exception as e:
        logger.error('当前页数错误:\n{}'.format(e))
        page = 1
    # 一开始默认加载第一页
    start_page = settings.ONE_PAGE_COUNT * (page - 1)
    end_page = start_page + settings.ONE_PAGE_COUNT

    # defer 排除不需要的字段,only 仅选择需要的字段
    articles = Article.objects.only('id', 'title', 'description', 'category_id', 'category__name', 'author__username', 'create_time',
                                    'read_num', 'like_num', 'cover_img').\
        select_related('author', 'category').values('id', 'title', 'description', 'category_id', 'category__name', 'author__username', 'create_time',
                                    'read_num', 'like_num', 'cover_img')[start_page:end_page]
    article_list = list(articles)
    return JsonResponse({"article_list": article_list})


# 自定义搜索view
class ArticleSearchView(SearchView):
    # 重写template变量，修改了搜索结果页面模板的位置。
    template = 'article/search_result.html'

    # 重写响应方式，如果请求参数q为空，返回模型article的热门新闻数据，否则根据参数q搜索相关数据
    # def create_response(self):
    #     kw = self.request.GET.get('q', '')
    #     if not kw:
    #         show_all = True
    #         hot_articles = Article.objects.only('id', 'cover_img', 'category', 'title', 'author', 'create_time',
    #                                         'read_num', 'like_num').all().order_by('-like_num')  # 逆序排列
    #
    #         paginator = Paginator(hot_articles, settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE)
    #         try:
    #             page = paginator.page(int(self.request.GET.get('page', 1)))
    #         except PageNotAnInteger:
    #             # 如果参数page的数据类型不是整型，则返回第一页数据
    #             page = paginator.page(1)
    #         except EmptyPage:
    #             # 用户访问的页数大于实际页数，则返回最后一页的数据
    #             page = paginator.page(paginator.num_pages)
    #         return render(self.request, self.template, locals())
    #     else:
    #         show_all = False
    #         qs = super(ArticleSearchView, self).create_response()
    #         return qs


import markdown
class ArticleDetailView(View):
    def get(self, request, article_id):
        # article = Article.objects.get(id=article_id)
        '''
            get_object_or_404方法，其作用就是当传入的pk对应的 Article 在数据库存在时，
            就返回对应的article，如果不存在，就给用户返回一个 404 错误，表明用户请求的文章不存在。
        '''
        article = get_object_or_404(Article, pk=article_id)

        # 文章每被浏览一次，则其阅读量 +1，即所谓的文章页面 PV（Page View）数。
        # article.read_num += 1
        # article.save()
        # 浏览量增加article自动完成
        article.increase_views()

        # 将阅读数也添加到redis中
        from django_redis import get_redis_connection

        conn_redis = get_redis_connection('default')
        # total_views = conn_redis.incr('article_{}_views'.format(article_id)) # incr 将 key 中储存的数字值增一。

        # zincrby的原型是zincrby(name,amount,value):根据amount所设定的步长值增加有序集合（name）中的value的数值
        # 实现了article_ranking中的article.id以步长1自增
        # 即访问文章一次, article_ranking就将文章ID的值增1
        conn_redis.zincrby('article_ranking', 1, article.id)

        # 上一篇，按照降序desc，将大于当前id过滤掉，即获取小于id的，然后用first获得第一个
        pre_article = Article.objects.only('title').order_by("-id").filter(id__lt=article_id).first()
        # 下一篇文章,升序asc，将小于当前id的过滤掉，取大于id的
        next_article = Article.objects.only('title').order_by("id").filter(id__gt=article_id).first()

        # 相关文章：1.按照标签；2. 按照分类；3.作者相关； 此处按照分类获取几个前端显示
        # 子查从
        category = article.category
        # relate_articles = category.article_set.only('id') _set反向查询法，以下另外种查询方法比这种查询效率快
        relate_articles = Article.objects.filter(category=category).exclude(id=article_id)[:5]

        # 查询多少个人参与，多少条评论
        comment_query_set = article.comment_set.filter(is_delete=False).order_by('-id')  # 反向查询

        # 统计id字段个数并用num_comments指定别名
        comments_dict = comment_query_set.aggregate(num_comments=Count('id'))
        # 统计user_id字段个数并用num_humans指定别名，distinct去重
        humans_dict = comment_query_set.aggregate(num_humans=Count('user_id', distinct=True))


        '''
        1. aggregate()为所有的QuerySet生成一个汇总值。返回结果类型为Dict，aggregate就是在django中实现聚合函数的，
            常见的聚合函数有AVG / COUNT / MAX / MIN /SUM 等。
        2. annotate()为每一个QuerySet在指定属性上生成汇总值，相当于GROUP BY。返回结果类型QuerySet。             
        '''

        # 取出所有的评论,列表套字典
        comment_list = list(comment_query_set.values())  # values将返回来的QuerySet中的Model转换为字典，list将QuerySet查询集转换为列表

        if request.user.is_authenticated:
            is_login = 1
        else:
            is_login = 0

        context = {
                       'comment_list': comment_list,
                       'article': article, 'pre_article': pre_article,
                       'next_article': next_article, 'relate_articles': relate_articles,
                       'comments_dict': comments_dict, 'humans_dict': humans_dict,
                       'is_login': is_login,
                   }

        # 后台传给js获取值，视图函数中的字典或列表要用 json.dumps()处理。在模板上可能要加 safe 过滤器。
        # return render(request, 'article.html', {'article': article, 'article_id': json.dumps(article.id)})
        return render(request, 'article/article.html', context=context)


class ArticleCommentView(View):
    def post(self, request, article_id):
        # 获取评论内容，当前用户，那篇文章
        new_content = request.POST.get('new_content', None)
        parent_id = request.POST.get('parent_id', None)

        from util import filter_words

        gfw = filter_words.DFAFilter()
        import os
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(BASE_DIR, 'util',"prohibited_words.txt")

        gfw.parse(path)
        result_content = gfw.filter(new_content)
        # print(new_content)
        # print(result_content)
        # result_content = new_content

        the_article = Article.objects.get(id=article_id)

        # 统计参与的人数，检查评论里面改文章是否有该用户
        is_exist = Comment.objects.filter(user=request.user, article=the_article).exists()
        if is_exist:
            add_human = 0
        else:
            add_human = 1
        # 保存到数据库中
        new_comment = Comment.objects.create(article=the_article, user=request.user, content=result_content,
                                             parent_id=parent_id)
        comment_id = new_comment.id

        # UTC时间+8个小时=系统时间
        local_time = new_comment.create_time + timedelta(hours=8)
        create_time = datetime.strftime(local_time, "%Y-%m-%d %H:%M:%S")

        # print(request.user.avatar)
        # 返回当前评论的内容给前端页面显示 , ImageFile类型不能被序列化，需要str（img对象）才可以
        return JsonResponse({'msg': '评论提交成功！', 'avatar': request.user.avatar, 'create_time': create_time,
                             'comment_id': comment_id,
                             'reply_nickname': request.user.nick_name, 'new_content': result_content,
                             'add_human': add_human})


def article_likes(request, article_id):
    article = get_object_or_404(Article, pk=article_id)

    # 判断是否同一个IP点赞，若是重复则不能继续点赞,反之点赞数也要相加
    if 'HTTP_X_FORWARDED_FOR' in request.META:  # request.META.has_key('HTTP_X_FORWARDED_FOR'):新版取消了has_key改用in判断
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']

    params = {'ip': ip, 'article_id': article_id}
    # 有就取这个数据，如果没有就创建数据,返回元组(<Column: 关于>, True)
    article_likes_tuple = ArticleLikeDetail.objects.get_or_create(**params)
    article_likes_instance, article_likes_created_bolean = article_likes_tuple
    if article_likes_created_bolean:  # 如果新创建了
        article.increase_likes()  # 点赞数+1
        add_flag = True
    else:  # 如果存在则
        add_flag = False

    likes_nums = article.like_num
    result = {'likes_nums': likes_nums, 'add_flag': add_flag}

    return JsonResponse(result)


@login_required
def notification(request):
    '''展示提示消息列表'''
    from datetime import datetime
    now_date = datetime.now()
    # get_p 查询子表，主表
    notifications = CommentNotification.objects.filter(get_p=request.user)
    notifications.update(is_read=True)

    context = {
        'notifications': notifications,
        'now_date': now_date
    }
    return render(request, 'user/notification.html', context=context)


@login_required
@require_POST
def mark_to_read(request):
    '''将一个消息标记为已读'''
    if request.is_ajax():
        data = request.POST
        id = data.get('id')
        info = get_object_or_404(CommentNotification, get_p=request.user, id=id)
        info.mark_to_read()
        return JsonResponse({'msg': 'mark success'})
    return JsonResponse({'msg': 'miss'})


@login_required
@require_POST
def mark_to_delete(request):
    '''将一个消息删除'''
    if request.is_ajax():
        data = request.POST
        id = data.get('id')
        info = get_object_or_404(CommentNotification, get_p=request.user, id=id)
        info.delete()
        return JsonResponse({'msg': 'delete success'})
    return JsonResponse({'msg': 'miss'})


