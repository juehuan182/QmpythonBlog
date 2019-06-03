from django.db import models
from django.core.validators import MinLengthValidator

from db.base_model import ModelBase
from user.models import Account

class Doc(ModelBase):
    title = models.CharField(max_length=30, validators=[MinLengthValidator(1),], unique=True, verbose_name='文档标题')
    desc = models.CharField(max_length=200, validators=[MinLengthValidator(1),], verbose_name='文档描述', help_text='文档描述')
    image_url = models.URLField(verbose_name='文档缩略图url', help_text='文档缩略图url')
    file_url = models.URLField(verbose_name='文档url', help_text='文档url')
    author = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, verbose_name='作者')

    class Meta:
        db_table = 'tb_doc'
        verbose_name = '文档'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
