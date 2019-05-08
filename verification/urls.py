from django.urls import path, include, re_path
from .views import graphCode, emailCode, resetPwdcode


app_name = 'verification'
urlpatterns = [

    # 发送图形验证码
    path('graph-code/', graphCode, name='graph-code'),

    # 邮箱验证码
    path('email-code/', emailCode, name='email-code'),

    # 找回密码验证码  resetPwdSendCode
    path('restPwd-code/', resetPwdcode, name='restPwd_code')


]
