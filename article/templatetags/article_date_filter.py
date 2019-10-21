from django import template
from datetime import datetime, timedelta
from django.utils import timezone


#生成一个注册
register = template.Library()

@register.filter
def date_format(val):

    #首先将utc时间转换为本地系统时间
    val = val + timedelta(hours=8)

    #判断一下，是不是时间日期类型
    if not isinstance(val, datetime):
        return val
    #获取当前时间
    time_now = timezone.now() + timedelta(hours=8)
    #文章发布时间val，当前时间减去新闻发布时间 得到间隔秒
    sec = (time_now - val).total_seconds()  #seconds是获取时间部分的差值，而total_seconds()是获取两个时间之间的总差

    #把秒转为刚刚、几分钟、几小时前
    if sec < 60:
        return '刚刚'
    elif 60 <= sec < 60*60:   #sec >= 60 and sec < 60*60
        mint = int(sec / 60)
        return '{}分钟前'.format(mint)
    elif 60*60 <=sec < 60*60*24:
        hour = int(sec / 60 / 60)
        return '{}小时前'.format(hour)
    elif 60*60*24 <= sec < 60*60*24*2:
        return '昨天'
    else:
        return val.strftime('%Y-%m-%d %H:%M:%S')


