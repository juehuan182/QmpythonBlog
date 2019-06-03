from django import template
from django_redis import get_redis_connection


#生成一个注册
register = template.Library()

@register.simple_tag
def show_cart_num(obj):
    if obj.is_authenticated:
        conn_redis = get_redis_connection('default')
        cart_key = 'cart_{}'.format(obj.id)
        cart_count = conn_redis.hlen(cart_key)  # hlen获取条目数据
    else:
        cart_count = 0

    return cart_count
