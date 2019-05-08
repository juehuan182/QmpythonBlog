from io import BytesIO
import json

from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q

from django_redis import get_redis_connection

from verification.captcha.captcha import Captcha
from verification import contants
from user.models import Account
from util import json_status, send_email
from celery_tasks.email.tasks import task_send_email

# Create your views here.
def graphCode(request):
    image_code_uuid = request.GET.get('image_code_uuid')

    # 生成验证码文本和验证码图片
    text, image = Captcha.gene_code()

    # BytesIO 二进制
    out = BytesIO()
    # 塞管道 保存文件 保存完成之后，处于末尾
    image.save(out, 'png')
    # 回到最开始位置 游标
    out.seek(0)

    # 返回一个 response JsonResponse(content_type) response
    resp = HttpResponse(content_type="image/png")
    # 前面已经塞进去 读出来
    resp.write(out.read())

    # 前面已经塞进去 读出来
    #  建立redis连接，并且将图片验证码保存到redis中
    conn_redis = get_redis_connection(alias='verify_code')
    image_key = 'image_key_{}'.format(image_code_uuid)
    # print(image_code_uuid, text.lower())
    conn_redis.setex(image_key, contants.IMAGE_CODE_REDIS_EXPIRES, text.lower()) # setex key seconds value  设置 key的同时，设置过期时间
    # 把验证码图片返回给前端, 返回一个 response JsonResponse(content_type) response
    return resp


def emailCode(request):
    json_data = request.body
    if not json_data:
        return json_status.params_error(message="参数错误")

    # 将json转化为dict
    dict_data = json.loads(json_data.decode('utf-8'))

    username = dict_data.get('username')
    email = dict_data.get('email')

    # 如果2个都存在
    if Account.objects.filter(username=username, email=email).exists():
        return json_status.params_error(message=u'用户名和邮箱都已使用，请重新输入！')

    # 如果username存在
    if Account.objects.filter(username=username).exists():
        return json_status.params_error(message=u'该用户名已使用，请重新输入！')

    # 如果is_email存在
    if Account.objects.filter(email=email).exists():
        return json_status.params_error(message=u'该邮箱已使用，请重新输入！')

    # 检查是否在60s内有发送记录
    conn_redis = get_redis_connection(alias='verify_code')

    email_flag_key = 'email_flag_key_{}'.format(email).encode('utf-8')

    email_flag = conn_redis.get(email_flag_key)
    if email_flag:
        return json_status.params_error(message='获取邮箱验证码过于频繁！')

    # 发送验证码给邮箱
    #  1. 同步发送邮件
    # result = send_email.send_email_code(email, 'register')
    # if result:
    #     return json_status.result(message='验证码已发送您邮箱，3分钟内有效，请注意查收！')
    # else:
    #     return json_status.params_error(message='验证码发送失败，请重新发送！')
    #  2. celery异步发送邮件，调用delay
    celery_res = task_send_email.delay(email, 'register')
    return json_status.result(message='验证码已发送成功，请注意查收！')


def resetPwdcode(request):
    json_data = request.body
    if not json_data:
        return json_status.params_error(message="参数错误")

    # 将json转化为dict
    dict_data = json.loads(json_data.decode('utf-8'))

    email = dict_data.get('email', '')

    if not Account.objects.filter(email=email).exists():
        return json_status.params_error(message="该邮箱未注册，请前往注册")

    # 检查是否在60s内有发送记录
    conn_redis = get_redis_connection(alias='verify_code')
    email_flag_key = 'email_flag_key_{}'.format(email).encode('utf-8')

    email_flag = conn_redis.get(email_flag_key)
    if email_flag:
        return json_status.params_error(message='获取邮箱验证码过于频繁！')

    # 发送验证码给邮箱
    #  1. 同步发送邮件
    # result = send_email.send_email_code(email, 'resetpwd')
    # if result:
    #     return json_status.result(message='验证码已发送您邮箱，3分钟内有效，请注意查收！')
    # else:
    #     return json_status.params_error(message='验证码发送失败，请重新发送！')

    #  2. celery异步发送邮件，调用delay
    task_send_email.delay(email, 'register')
    return json_status.result(message='验证码已发送成功，请注意查收！')




