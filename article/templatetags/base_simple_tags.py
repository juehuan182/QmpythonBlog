from django import template
from article.models import Article, Tag, Column, ArticleRecommend
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
def get_hot_articles():
    return Article.objects.only('like_num').order_by('-like_num')[:6]


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


# 统计总文章数
@register.simple_tag
def get_total_article():
    return Article.objects.count()


# 统计访问量
@register.simple_tag
def get_access_nums():
    return Access.objects.count()


@register.simple_tag
def get_friend_links():
    friendLinks = FriendLink.objects.filter(is_delete=False)
    return friendLinks
