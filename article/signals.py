from django.dispatch import receiver
from django.db.models.signals import post_save

from article.models import Comment, CommentNotification


# 第一步，编写receiver并绑定到signal

@receiver(post_save, sender=Comment, dispatch_uid="comment_post_save") #dispatch_uid 确保此receiver 只调用一次
def notify_handler(sender, instance=None, created=False, **kwargs):
    # print('消息通知')
    current_instance = instance
    the_article = current_instance.article
    create_p = current_instance.user

    # True if a new record was created.判断是否创建评论了
    if created:
        if current_instance.parent_id: #如果评论是一个回复评论，则同时通知给文章作者和回复的评论人，如果2者相等，则只通知一次
            if the_article.author == current_instance.parent.user:
                get_p = current_instance.parent.user
                if create_p != get_p:  #如果不是回复自己的
                    new_notify = CommentNotification(create_p=create_p, get_p=get_p, comment=current_instance)
                    new_notify.save()
            else:  #如果文章作者和父评论是不同的人，则都要通知到位
                get_p1 = the_article.author  #获取文章作者
                if create_p != get_p1: #如果不是自己
                    new1 = CommentNotification(create_p=create_p, get_p=get_p1, comment=current_instance)  #通知文章作者
                    new1.save()
                get_p2 = current_instance.parent.user #获取父评论
                if create_p != get_p2:
                    new2 = CommentNotification(create_p=create_p, get_p=get_p2, comment=current_instance)  #通知被评论的人
                    new2.save()
        else:   #如果评论是一级评论
            get_p = the_article.author
            if create_p != get_p:  #而且不是回复其他评论并且不是作者自评，则直接通知给文章作者
                new_notify = CommentNotification(create_p=create_p, get_p=get_p, comment=current_instance)
                new_notify.save()

# 要接收信号，请使用Signal.connect()方法注册一个接收器。当信号发送后，会调用这个接收器。
#post_save.connect(notify_handler, sender=Comment, weak=False, dispatch_uid='comment_notification')
'''
post_save¶
django.db.models.signals.post_save，在save()方法结束时发送 。

使用此信号发送的参数：
sender   模型类。
instance    正在保存的实际实例。
created 布尔值;    True如果创建了新记录。
raw 布尔值;    True如果模型完全按照提供的方式保存（即加载夹具时）。不应该查询/修改数据库中的其他记录，因为数据库可能尚未处于一致状态。
using   正在使用的数据库别名。
update_fields   要传递给更新的字段集Model.save()，或者None 如果update_fields未传递给它save()。

'''
'''
Django自带的models提供了几个信号，它们位于django.db.models.signals。
pre_save:调用model的save()方法前发送信号

post_save:调用model的save()方法后发送信号

pre_delete:调用model活着QuerySets的delete()方法前发送信号

post_delete：同理，调用delete()后发送信号

m2m_changed:当一个模型上的ManyToManyField字段被改变的时候发送信号
'''