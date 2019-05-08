import random
import logging

from django.core.mail import send_mail
from django_redis import get_redis_connection
from django.conf import settings

from verification import contants

# 导入日志器
logger = logging.getLogger('django')


# 在python中的random.randint(a,b)用于生成一个指定范围内的整数，生成的随机数n: a <= n <= b
# 定义一个随机字符串的方法
def random_str(random_length=8):
    active_code = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlNnMmOoPpQqRrSsTtUuVvWwXxYyZz012346789'
    length = len(chars) - 1

    # 随机生成激活码
    for i in range(0, random_length):  # 需要生成random_length位随机数，循环对应多少次，每次从chars中读取一个字符，拼接成多少位
        active_code += chars[random.randint(0, length)]  # range：左闭右开；randint：左右皆闭;[]：左闭右开

    return active_code


# 定义一个发送邮件
def send_email_code(email, send_type='register'):
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

    # 保存缓存
    # mcache.set_key(email, code.lower(), 120)
    conn_redis = get_redis_connection(alias='verify_code')
    pl = conn_redis.pipeline()

    # 创建一个在60s以内是否有发送邮件记录的标记
    email_flag_key = "email_flag_key_{}".format(email).encode('utf-8')

    # 创建保存邮箱验证码的标记key
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
        logger.debug("发送邮箱验证码[异常][email: %s, message: %s]" % (email, e))

        return None  # 如果为0或者抛出异常，返回None

    else:  # 如果try里面的语句可以正常执行，那么就执行else里面的语句（相当于程序没有碰到致命性错误）
        if send_status:  # 成功返回1，不成功返回0或者报错
            logger.info("发送验证码邮件[正常][email: %s email_code: %s]" % (email, code))
            return send_status
        else:
            logger.warning("发送验证码邮件[失败][email: %s]" % email)

            return None


'''
1.单发send_mail()方法返回值将是成功发送出去的邮件数量（只会是0或1，因为它只能发送一封邮件）。
2.群发 send_mass_mail()，用来处理大批量邮件任务。返回值是成功发送的邮件数量。
使用send_mail()方法时，每调用一次，它会和SMTP服务器建立一次连接，也就是发一次连一次，效率很低。
而send_mass_mail()，则只建立一次链接，就将所有的邮件都发送出去，效率比较高。

需要提醒的是，接收方的邮件服务商不一定支持多媒体邮件，可能为了安全，也许是别的原因。
为了保证邮件内容能被阅读，最好2种格式一起发送纯文本邮件。
'''
