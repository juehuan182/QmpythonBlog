# Generated by Django 2.2.7 on 2019-12-30 07:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('article', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='commentnotification',
            name='create_p',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notification_create', to=settings.AUTH_USER_MODEL, verbose_name='提示创建者'),
        ),
        migrations.AddField(
            model_name='commentnotification',
            name='get_p',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notification_get', to=settings.AUTH_USER_MODEL, verbose_name='提示接收者'),
        ),
        migrations.AddField(
            model_name='comment',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='article.Article', verbose_name='评论文章'),
        ),
        migrations.AddField(
            model_name='comment',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='article.Comment', verbose_name='父级评论'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='用户'),
        ),
        migrations.AddField(
            model_name='category',
            name='column',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='article.Column', verbose_name='所属栏目'),
        ),
        migrations.AddField(
            model_name='articlerecommend',
            name='article',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='article.Article', verbose_name='文章'),
        ),
        migrations.AddField(
            model_name='articlelikedetail',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='article.Article', verbose_name='文章'),
        ),
        migrations.AddField(
            model_name='article',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='articles', to=settings.AUTH_USER_MODEL, verbose_name='作者'),
        ),
        migrations.AddField(
            model_name='article',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='article.Category', verbose_name='所属类别'),
        ),
        migrations.AddField(
            model_name='article',
            name='tag',
            field=models.ManyToManyField(to='article.Tag'),
        ),
    ]
