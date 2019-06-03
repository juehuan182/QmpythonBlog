from django.db import models
from django.core.validators import MinLengthValidator
from django.utils.html import strip_tags

import markdown


from django.conf import settings

from db.base_model import ModelBase
from user.models import Account

# Create your models here.


# 栏目
class Column(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name='栏目')
    link_url = models.URLField(verbose_name= '链接')
    index = models.IntegerField(verbose_name='位置')

    class Meta:  # 模型元选项
        db_table = 'tb_column'   # 在数据库中的表名，否则Django自动生成为app名字_类名
        ordering = ['index']
        verbose_name = '栏目'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

# 分类
class Category(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name=u'分类')

    #多对一关系，会在数据库中生成column_id的字段,注意Django只有多对一关系，站在多的角度去看待
    column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name='categories', verbose_name=u'所属栏目')

    class Meta:
        db_table = 'tb_category'
        ordering = ['id']
        verbose_name = u'类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 标签
class Tag(models.Model):
    name = models.CharField(verbose_name=u'标签', max_length=20, unique=True)

    class Meta:
        db_table = 'tb_tag'
        verbose_name = u'标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

# 文章
class Article(ModelBase):
    # null是在数据库上表现NULL，而不是一个空字符串，所以对空字符串的限制，还需要通过blank，是否能为空字符串控制
    title = models.CharField(max_length=35, validators=[MinLengthValidator(1), ], unique=True, verbose_name='标题')
    keywords = models.CharField(max_length=50, validators=[MinLengthValidator(1), ], verbose_name='关键词')
    description = models.CharField(verbose_name='描述', max_length=120, validators=[MinLengthValidator(1), ], blank=True)  #选填，如果不填默认抓取正文前54个字
    content = models.TextField(verbose_name='内容')
    cover_img = models.URLField(verbose_name='封面图', blank=True)
    #PositiveIntegerField，该类型的值只允许为正整数或 0，毕竟阅读量不可能为负值。
    read_num = models.PositiveIntegerField(verbose_name='浏览量', default=0)
    like_num = models.IntegerField(verbose_name='点赞数', default=0)

    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, verbose_name='所属类别')  #多对一关系

    tag = models.ManyToManyField(Tag) #多对多关系

    #当外键指向的数据对象被删除“on_delete”时，models.DOTHING，即用户删除时，文章不做任何处理
    author = models.ForeignKey(Account, on_delete=models.DO_NOTHING, related_name='articles', verbose_name='作者')

    class Meta:
        db_table = 'tb_article'
        ordering = ['-create_time']
        verbose_name = u'文章'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    def increase_views(self):
        self.read_num += 1
        #一旦用户访问谋篇文章，这时就应该将 views 的值 +1，这个过程最好由 article 模型自己来完成，因此再给模型添加一个自定义的方法
        #使用了 update_fields 参数来告诉 Django 只更新数据库中 views 字段的值，以提高效率。默认save方法会更新所有字段不管有没有改变
        self.save(update_fields=['read_num'])

    def increase_likes(self):
        self.like_num += 1
        self.save(update_fields=['like_num'])  #只更新like_num字段，减轻服务器工作压力

    def save(self, *args, **kwargs):
        #如果没有填写描述
        if not self.description:
            # 首先实例化一个markdown类，用于将markdown文本渲染成HTML文本
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ])
            # strip_tags去掉HTML文本的全部HTML标签, 从文本描述取前120个字符给description
            self.description = strip_tags(md.convert(self.content))[:120]   #strip_tags 去掉 HTML 文本的全部 HTML 标签

        if not self.cover_img: # 如果为为空则给个默认值
            self.cover_img = settings.SITE_DOMAIN + '/static/image/article/article_cover.jpg'

        # 调用父类的 save 方法将数据保存到数据库中
        super(Article, self).save(*args, **kwargs)

#点赞
class ArticleLikeDetail(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name=u'文章')
    ip = models.GenericIPAddressField(verbose_name=u'访问IP')

    class Meta:
        db_table = 'tb_article_like_detail'
        verbose_name = u'点赞详情'


# 推荐文章
class ArticleRecommend(models.Model):
    PRI_CHOICES = ((1, '第一级'), (2, '第二级'), (3, '第三级'), (4, '第四级'), (5, '第五级'), (6, '第六级'))

    article = models.OneToOneField(Article, on_delete=models.CASCADE, verbose_name=u'文章')
    priority = models.IntegerField(verbose_name=u'优先级', choices=PRI_CHOICES)

    class Meta:
        db_table = 'tb_article_recommend'
        # 默认是从小到大 - (取反)
        ordering = ['priority']
        verbose_name = u'推荐文章'
        verbose_name_plural = verbose_name


class Comment(models.Model):
    content = models.CharField(max_length=400, verbose_name=u'评论内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'评论时间')
    # self 自关联
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'父级评论') #不一定存在
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name=u'评论文章')
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, verbose_name=u'用户')
    is_delete = models.BooleanField(default=False, verbose_name='是否显示')

    class Meta:
        db_table = 'tb_comment'
        verbose_name = u'评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content[:50]


# 评论回复通知
class CommentNotification(models.Model):
    create_p = models.ForeignKey(Account, verbose_name='提示创建者', related_name='notification_create', on_delete=models.CASCADE)
    get_p = models.ForeignKey(Account, verbose_name='提示接收者', related_name='notification_get', on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, verbose_name='所属评论', related_name='the_comment', on_delete=models.CASCADE)
    create_time = models.DateTimeField(verbose_name='提示时间', auto_now_add=True)
    is_read = models.BooleanField(verbose_name='是否已读', default=False)

    def mark_to_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])   #保存的时候只更改is_read字段；

    class Meta:
        db_table = 'tb_comment_notification'
        ordering = ['-create_time']
        verbose_name = '评论回复通知'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{}@了{}'.format(self.create_p, self.get_p)

class Advertising(ModelBase):
    POSITION_CHOICES = (('top_left', '左上'), ('top_right', '右上'), ('right', '右'), ('bottom', '下'))
    name = models.CharField(max_length=50, verbose_name=u'名称')
    image_url = models.URLField(verbose_name=u'图片')
    link_to = models.URLField(verbose_name=u'网址')
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, verbose_name=u'位置')
    end_time = models.DateField(verbose_name=u'结束日期')
    click_num = models.IntegerField(verbose_name=u'点击量', default=0)
    sort = models.IntegerField(verbose_name=u'排序', default=0)

    class Meta:
        db_table = 'tb_advertising'
        ordering = ['sort']
        verbose_name = '广告'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


