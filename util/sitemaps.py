from django.contrib.sitemaps import Sitemap
from django.db.models.aggregates import Count

from article.models import Article, Category, Tag


# 文章聚类
class ArticleSitemap(Sitemap):
    changefreq = "weekly"  # 页面可能发生更改的频率
    priority = 1.0  # 此网址的优先级与您网站上其他网址的优先级相关

    def items(self):   # items()方法返回了在这个站点地图中所包含对象的查询集QuerySet,
        return Article.objects.all()

    def lastmod(self, obj):  # 接收items()返回的每一个对象并且返回对象最后修改时间
        return obj.update_time

    def location(self, obj):
        return '/articles/{0}/'.format(obj.id)

# 分类聚类
class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Category.objects.annotate(total_num=Count('article')).filter(total_num__gt=0)

    def lastmod(self, obj):
        return obj.article_set.first().create_time

    def location(self, obj):
        return '/categories/{0}/'.format(obj.id)

# 标签聚类
class TagSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Tag.objects.annotate(total_num=Count('article')).filter(total_num__gt=0)

    def lastmod(self, obj):
        return obj.article_set.first().create_time

    def location(self, obj):
        return '/tags/{0}/'.format(obj.id)

'''
这里从 Sitemap 类继承一个类，实现 items 方法，该方法返回所有要加入 Sitemap 的数据
，属性changefreq、priority 和方法 location、lastmod 分别对应 Sitemap 标准 xml 文档中的相应字段。

changfreq：取值范围为：always、hourly、daily、weekly、monthly、yearly、never，可根据实际情况进行设置

priority：取值范围为0.4-1.0，如果不设置则默认值为0.5

location：用于定制地图项的url。如果不实现该方法，则必须实现地图对应model的get_absolute_url方法，实现该方法后则会优先采用该方法返回的url：
如果未提供location，框架将调用items()返回的每个对象上的get_absolute_url()方法。
'''