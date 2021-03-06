# Generated by Django 2.2.7 on 2019-12-30 07:58

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Advertising',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
                ('name', models.CharField(max_length=50, verbose_name='名称')),
                ('image_url', models.URLField(verbose_name='图片')),
                ('link_to', models.URLField(verbose_name='网址')),
                ('position', models.CharField(choices=[('top_left', '左上'), ('top_right', '右上'), ('right', '右'), ('bottom', '下')], max_length=10, verbose_name='位置')),
                ('end_time', models.DateField(verbose_name='结束日期')),
                ('click_num', models.IntegerField(default=0, verbose_name='点击量')),
                ('sort', models.IntegerField(default=0, verbose_name='排序')),
            ],
            options={
                'verbose_name': '广告',
                'verbose_name_plural': '广告',
                'db_table': 'tb_advertising',
                'ordering': ['sort'],
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
                ('title', models.CharField(max_length=35, unique=True, validators=[django.core.validators.MinLengthValidator(1)], verbose_name='标题')),
                ('keywords', models.CharField(max_length=50, validators=[django.core.validators.MinLengthValidator(1)], verbose_name='关键词')),
                ('description', models.CharField(blank=True, max_length=120, validators=[django.core.validators.MinLengthValidator(1)], verbose_name='描述')),
                ('content', models.TextField(verbose_name='内容')),
                ('cover_img', models.URLField(blank=True, verbose_name='封面图')),
                ('read_num', models.PositiveIntegerField(default=0, verbose_name='浏览量')),
                ('like_num', models.IntegerField(default=0, verbose_name='点赞数')),
            ],
            options={
                'verbose_name': '文章',
                'verbose_name_plural': '文章',
                'db_table': 'tb_article',
                'ordering': ['-create_time'],
            },
        ),
        migrations.CreateModel(
            name='ArticleLikeDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField(verbose_name='访问IP')),
            ],
            options={
                'verbose_name': '点赞详情',
                'db_table': 'tb_article_like_detail',
            },
        ),
        migrations.CreateModel(
            name='ArticleRecommend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.IntegerField(choices=[(1, '第一级'), (2, '第二级'), (3, '第三级'), (4, '第四级'), (5, '第五级'), (6, '第六级')], verbose_name='优先级')),
            ],
            options={
                'verbose_name': '推荐文章',
                'verbose_name_plural': '推荐文章',
                'db_table': 'tb_article_recommend',
                'ordering': ['priority'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True, verbose_name='分类')),
            ],
            options={
                'verbose_name': '类别',
                'verbose_name_plural': '类别',
                'db_table': 'tb_category',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Column',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True, verbose_name='栏目')),
                ('link_url', models.URLField(verbose_name='链接')),
                ('index', models.IntegerField(verbose_name='位置')),
            ],
            options={
                'verbose_name': '栏目',
                'verbose_name_plural': '栏目',
                'db_table': 'tb_column',
                'ordering': ['index'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=400, verbose_name='评论内容')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='评论时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否显示')),
            ],
            options={
                'verbose_name': '评论',
                'verbose_name_plural': '评论',
                'db_table': 'tb_comment',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True, verbose_name='标签')),
            ],
            options={
                'verbose_name': '标签',
                'verbose_name_plural': '标签',
                'db_table': 'tb_tag',
            },
        ),
        migrations.CreateModel(
            name='CommentNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='提示时间')),
                ('is_read', models.BooleanField(default=False, verbose_name='是否已读')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='the_comment', to='article.Comment', verbose_name='所属评论')),
            ],
            options={
                'verbose_name': '评论回复通知',
                'verbose_name_plural': '评论回复通知',
                'db_table': 'tb_comment_notification',
                'ordering': ['-create_time'],
            },
        ),
    ]
