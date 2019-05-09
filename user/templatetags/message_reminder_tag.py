from django import template

from article.models import CommentNotification


register = template.Library()

@register.simple_tag
def message_reminder_count(instance):
    reminder_nums = CommentNotification.objects.filter(get_p=instance, is_read=False).count()
    return reminder_nums



