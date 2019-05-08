from django import template


#生成一个注册
register = template.Library()

@register.filter
def display_status(val):

    if val:
        return '停用'

    return '正常'