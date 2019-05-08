import os

from django.db import models

from django.db import models
from django.core.validators import MinLengthValidator

from article.models import ModelBase


def lectuer_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format('avatar_'+instance.id, ext)

    return os.path.join('avatar/lectuer/', instance.id, filename)

class Lectuer(ModelBase):
    name = models.CharField(max_length=150, verbose_name='姓名', help_text='姓名')
    positional_titles = models.CharField(max_length=150, verbose_name='职称', help_text='职称')
    profile = models.TextField(verbose_name='简介', help_text='简介')
    avatar_url = models.ImageField(upload_to='lectuer_directory_path',default='avatar/qmpython_avatar.png', blank=True, max_length=100, verbose_name=u'头像', help_text='头像')

    class Meta:
        db_table = 'tb_lectuer'
        verbose_name = '讲师'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CourseCategory(ModelBase):
    name = models.CharField(max_length=100, verbose_name="课程分类名", help_text='课程分类名')

    class Meta:
        db_table = 'tb_course_category'
        verbose_name = '课程分类'
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.name

class Course(ModelBase):
    title = models.CharField(max_length=50, validators=[MinLengthValidator(1), ], verbose_name="课程名", help_text='课程名', unique=True)
    cover_url = models.URLField(verbose_name="课程封面图URL", help_text='课程封面图URL')
    video_url = models.URLField(verbose_name="课程视频URL", help_text='课程视频URL')
    duration = models.FloatField(default=0.0, verbose_name="课程时长", help_text='课程时长')
    desc = models.TextField(verbose_name="课程简介", help_text='课程简介')
    outline = models.TextField(verbose_name="课程大纲", help_text='课程大纲')

    lectuer = models.ForeignKey(Lectuer, on_delete=models.CASCADE)
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE)

    class Meta:
        db_table = "tb_course"
        verbose_name = "课程"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


