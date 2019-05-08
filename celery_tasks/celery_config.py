from datetime import timedelta


# Broker配置，使用Redis作为消息中间件，存放broker消息队列
broker_url = "redis://127.0.0.1:6379/4"

# BACKEND配置，这里使用redis，存放执行结果
result_backend = "redis://127.0.0.1:6379/5"

CELERYBEAT_SCHEDULE = {
    'ptask': {
        'task': 'tasks.period_task',
        'schedule': timedelta(seconds=5), # 间隔执行的时间
    },
}

CELERY_TIMEZONE = 'Asia/Shanghai'