import os

from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
from django.conf import settings

from db.base_model import ModelBase


'''
继承AbstractUser，在syncdb时不再建立auth_user表，而是建立了以你的模块名为表名的表，你只需要在你的Model里增加你需要的字段即可
AbstractUser 是一个抽象类
'''

# 动态定义上传路径
def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format('avatar_'+instance.id, ext)

    return os.path.join('avatar', instance.id, filename)

    #return '{0}/{1}/{2}'.format(instance.id, 'avatar', filename) # 返回最后的路径
    #上述案例显然还有一个问题，不同系统路径分隔符 / 和\是不一样的，为保证代码在不同系统中能重用，
    # 更好的方式是使用python的os模块来拼接路径。


#用户信息
class Account(AbstractUser):
    SEX_CHOICES = (('m', u'男'), ('f', u'女'), ('n', u'未知'))

    # Django模型中的ImageField和FileField的upload_to选项是必填项，其存储路径是相对于MEIDA_ROOT而来的。
    # 要在模板中使用该图片，应该使用avatar.url
    # 如果想要使用ImageField，必须要安装Pillow库
    # avatar = models.ImageField(upload_to='user_directory_path', default='avatar/qmpython_avatar.png', blank=True, max_length=100, verbose_name=u'头像')

    avatar = models.URLField(default= settings.MEDIA_URL + 'avatar/qmpython_avatar.png', blank=True, max_length=100, verbose_name='头像')
    nick_name = models.CharField(max_length=16, unique=True, verbose_name=u'昵称')
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, blank=True, verbose_name=u'性别')
    mobile = models.CharField(max_length=11, blank=True, verbose_name=u'手机')
    qq = models.CharField(max_length=15, null=True, blank=True, verbose_name=u'QQ') #CharField类型时必须设置max_length
    birthday = models.DateField(null=True, blank=True, verbose_name=u'生日')
    profile = models.CharField(max_length=400, null=True, blank=True, verbose_name=u'简介') #可为空，可为空白字符

    class Meta:
        db_table = 'tb_account'
        verbose_name = u'用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.nick_name:  #  如果没有填写昵称，则和用户名一样
            self.nick_name = self.username
        super(Account, self).save(*args, **kwargs)

    def get_groups_name(self):  # 统计每个用户所有的角色，通过在模型中定义这样可以达到类似按用户分组统计效果
        groups_name_list = [group.name for group in self.groups.all()]

        return '、'.join(groups_name_list) #列表通过|拼接成字符串


class AccountAddress(ModelBase):
    """
    用户收货地址模型
    """
    user = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='用户')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    address = models.CharField(max_length=256,verbose_name='收件地址')
    zip_code = models.CharField(max_length=6, null=True, verbose_name='邮编')
    phone = models.CharField(max_length=11, verbose_name='手机号码')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.address










#在django 2中，models中on_delete=models.XXX不再是默认选项，需要显性指定
#新版django中，orm多对多外健不再用=等赋值,改为set方法
#新版python中字典的has_key方法取消，建议用”str” in dict判断
'''
new_list = [obj1, obj2, obj3]
e.related_set = new_list ===》 e.related_set.set([obj1, obj2, obj3]
'''
#在django升级之后，makemigration重作,migrate可能需要手工增加on_delete=models.XXX

#访问量统计
class Access(models.Model):
    access_ip = models.GenericIPAddressField(verbose_name=u'访问IP')
    access_url = models.CharField(max_length=30, verbose_name=u'访问路径')
    access_time = models.DateTimeField(auto_now_add=True, verbose_name=u'访问时间')

    class Meta:
        db_table = 'tb_access_log'
        verbose_name = u'访问记录'
        verbose_name_plural = verbose_name


#友情链接
class FriendLink(models.Model):
    name = models.CharField(max_length=20, verbose_name='名称')
    link_url = models.URLField(max_length=100, verbose_name='网址')
    is_delete = models.BooleanField(default=False, verbose_name='是否删除')

    class Meta:
        db_table = 'tb_friend_link'
        verbose_name = u'友情链接'
        verbose_name_plural = verbose_name


# 第三方登录
class OAuthEx(models.Model):
    TYPE_CHOICES = (('1', 'qq'), ('2', 'weibo'), ('3', 'github'))
    user = models.ForeignKey(Account, on_delete=models.DO_NOTHING)
    openid = models.CharField(max_length=70)
    loginType = models.CharField(max_length=1, choices=TYPE_CHOICES)

    class Meta:
        db_table = 'tb_oauth_ex'
        verbose_name = '第三方账户'
        verbose_name_plural = verbose_name
