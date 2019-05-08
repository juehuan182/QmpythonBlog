import logging

from celery_tasks.celery_main import app

from django.conf import settings
from django.template import loader


from article.models import Article, Advertising


# 导入日志器
logger = logging.getLogger('qmpython')

@app.task
def task_generate_static_index_html():
    '''产生首页静态页面'''

    # 获取文章
    articles = Article.objects.only('id', 'cover_img', 'category', 'title', 'author', 'create_time',
                                    'read_num', 'like_num').order_by('-create_time')  # 逆序排列
    # 最新发布
    new_articles = articles[0:settings.ONE_PAGE_COUNT]
    # 轮播图
    Advertisings = Advertising.objects.only('id').filter(is_delete=False)
    leftAdvertisings = Advertisings.filter(position='top_left')
    rightAdvertisings = Advertisings.filter(position='top_right')

    # 获取首页标题，META关键词，META描述
    import configparser
    import os
    config = configparser.ConfigParser()
    conf_path = os.path.join(settings.BASE_DIR, 'util', 'web_info.ini')
    config.read(conf_path, encoding='utf-8')
    section_node = config.sections()[0]
    web_title = config.get(section_node, "WEB_SITE_TITLE")
    web_keywords = config.get(section_node, "WEB_SITE_KEYWORDS")
    web_desc = config.get(section_node, "WEB_SITE_DESC")

    context = {'new_articles': new_articles,
               'leftAdvertisings': leftAdvertisings,
               'rightAdvertisings': rightAdvertisings,
               'web_title': web_title,
               'web_keywords': web_keywords,
               'web_desc': web_desc
               }

    # return render(request, 'index.html', context=context)
    # 使用模板
    # 1.加载模板文件,返回模板对象
    temp = loader.get_template('static_index.html')
    # 2.模板渲染
    static_index_html = temp.render(context)
    # print(static_index_html)
    # 生成首页对应静态文件
    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')
    with open(save_path, 'w') as f:
        f.write(static_index_html)



