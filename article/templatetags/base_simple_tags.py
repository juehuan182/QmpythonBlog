from django import template
from django_redis import get_redis_connection
from django.db.models import Count

from article.models import Article, Tag, Column, Category, ArticleRecommend
from user.models import Access, FriendLink


register = template.Library()

#获取导航栏目
@register.simple_tag
def get_nav_columns():
    # 获取栏目
    columns = Column.objects.all()
    return columns


# 热门文章5篇，根据浏览量来统计
@register.simple_tag
def get_hot_articles(num):
    '''获取排行前num位的数据'''

    conn_redis = get_redis_connection(alias='default')

    # 得到article_ranking中排序前num名对象
    # 以 0 表示有序集第一个成员，以 1 表示有序集第二个成员
    # 以 -1 表示最后一个成员， -2 表示倒数第二个成员
    article_ranking = conn_redis.zrange('article_ranking', 0, -1, desc=True)[:num]
    #print(article_ranking)

    if article_ranking:
        #print(article_ranking) # [b'14', b'10', b'15', b'11']
        # 得到前num名文章ID
        article_ranking_ids = [int(id) for id in article_ranking ]
        #print(article_ranking_ids) # [14, 10, 15, 11]

        # 查询出id在article_ranking_ids范围内所有文章对象,并生成列表
        hot_viewed = list(Article.objects.only('id').filter(id__in=article_ranking_ids))
        # 对所得到的列表进行排序
        hot_viewed.sort(key=lambda x: article_ranking_ids.index(x.id))
    else:
        hot_viewed = Article.objects.only('like_num').order_by('-like_num')[:num]

    #print(hot_viewed) # [<Article: 测试>, <Article: 文章标题文章标题>, <Article: 测试2>, <Article: RESTful架构>]

    return hot_viewed


# 推荐文章5篇
@register.simple_tag
def get_recommend_articles():
    return ArticleRecommend.objects.only('article').select_related('article').order_by('priority')


#标签
@register.simple_tag
def get_tags():
    # 标签
    tags = Tag.objects.only('id')
    # 使用annotate
    # tags = Tag.objects.annotate(num_posts=Count('article')).filter(num_posts__gt=0)
    return tags

# 分类
@register.simple_tag
def get_categories():
    return Category.objects.count()


# 统计总文章数
@register.simple_tag
def get_total_article():
    return Article.objects.only('is_delete').filter(is_delete=False).count()


# 统计访问量
@register.simple_tag
def get_access_nums():
    return Access.objects.count()


@register.simple_tag
def get_friend_links():
    friendLinks = FriendLink.objects.filter(is_delete=False)
    return friendLinks
