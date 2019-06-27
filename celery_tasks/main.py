import os

from celery import Celery

# 设置django环境，celery 运行时需要读取django中的信息
# if not os.getenv('DJANGO_SETTINGS_MODULE'):
#     os.environ['DJANGO_SETTINGS_MODULE'] = 'QmpythonBlog.settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QmpythonBlog.settings')

# 创建一个Celery类的实例对象
app = Celery('QmpythonBlog')

#  从单独的配置模块中加载配置，导入celery配置
app.config_from_object('celery_tasks.config')

# 自动搜索任务
app.autodiscover_tasks(['celery_tasks.email', ])


