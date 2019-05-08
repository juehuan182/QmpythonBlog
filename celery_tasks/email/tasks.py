import logging
import random


from celery_tasks.celery_main import app

from django.core.mail import send_mail
from django_redis import get_redis_connection
from django.conf import settings

from verification import contants

# 导入日志器
logger = logging.getLogger('qmpython')


def random_str(random_length=8):
    active_code = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlNnMmOoPpQqRrSsTtUuVvWwXxYyZz012346789'
    length = len(chars) - 1

    # 随机生成激活码
    for i in range(0, random_length):  # 需要生成random_length位随机数，循环对应多少次，每次从chars中读取一个字符，拼接成多少位
        active_code += chars[random.randint(0, length)]  # range：左闭右开；randint：左右皆闭;[]：左闭右开

    return active_code

# 创建任务函数
@app.task
def task_send_email(email, send_type='register'):
    import time
    time.sleep(10)  # 这里休眠10s中，看是否会前面发送的时候卡主

    if send_type == 'register':
        code_len = 6
    elif send_type == 'resetpwd':
        code_len = 6
    else:
        code_len = 4

    code = random_str(code_len)
    subject = ''  # 主题
    text_message = ''  # 正文
    html_message = ''  # html格式正文

    if send_type == 'register':
        # print('register')
        subject = u'全民python-注册验证码'
        text_message = u'【全民python】您的注册验证码：{0}，请勿将此验证码告知他人，若非本人操作，请联系或者忽略，3分钟内有效！'.format(code)  # text格式
        html_message = u'【全民python】您的注册验证码：{0}，请勿将此验证码告知他人，若非本人操作，请联系或者忽略，3分钟内有效！'.format(code)  # html格式方便点击链接

    elif send_type == 'resetpwd':
        subject = u'全民python-找回密码验证码'
        text_message = u'【全民python】找回登录密码的验证码：{0}，请勿将此验证码告知他人，若非本人操作，请联系或者忽略，3分钟内有效！'.format(code)
        html_message = u'<p>【全民python】找回登录密码的验证码：{0}，请勿将此验证码告知他人，若非本人操作，请联系或者忽略，3分钟内有效！</p>'.format(code)
    else:
        subject = ''
        text_message = ''
        html_message = ''

    conn_redis = get_redis_connection(alias='verify_code')
    pl = conn_redis.pipeline()

    email_flag_key = "email_flag_key_{}".format(email).encode('utf-8')

    email_code_key = "email_code_key{}".format(email).encode('utf-8')

    # 在此处设置为True会出现bug
    try:
        pl.setex(email_flag_key, contants.SEND_CODE_INTERVAL, 1)  # 是否已发送标志
        pl.setex(email_code_key, contants.EMAIL_CODE_REDIS_EXPIRES, code.lower())  # 保存验证码
        # 让管道通知redis执行命令
        pl.execute()
    except Exception as e:
        logger.debug("redis 执行出现异常:{}".format(e))
        return None

    logger.info("email code:{}".format(code))

    try:
        send_status = send_mail(subject, text_message, settings.EMAIL_FROM, [email],
                                html_message)  # 如果提供了html_message，可以发送带HTML代码的邮件。
    except Exception as e:
        logger.debug("发送邮箱验证码[异常][mobile: %s, message: %s]" % (email, e))

        #return None  # 如果为0或者抛出异常，返回None

    else:  # 如果try里面的语句可以正常执行，那么就执行else里面的语句（相当于程序没有碰到致命性错误）
        if send_status:  # 成功返回1，不成功返回0或者报错
            logger.info("发送验证码邮件[正常][email: %s email_code: %s]" % (email, code))
            #return send_status
        else:
            logger.warning("发送验证码邮件[失败][email: %s]" % email)

            #return None



