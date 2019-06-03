from django.contrib import admin
from django.urls import path, include, re_path

from .views import RegisterView, checkUsername, checkEmail, LoginView,\
    LogoutView, RegisterView, UserProfileView, UserPasswordView, ResetPwdView, ConfirmView, checkVerifyCode, \
    upload_avatar, history, history_del, UserOrderView, UserOrderNotifyView, UserOrderReturnView, AddressView,\
    bind_account, BindLoginView, bind_success, qq_login, qq_callback, github_login,\
    github_callback, weibo_login, weibo_callback


app_name = 'user'  #需要提供namespace命名空间时,需要添加在应用的urls.py文件中添加 app_name = "appname"

urlpatterns = [
    # 用户注册
    # url(r'register/?$', RegisterView.as_view(), name='register'), #? 匹配前面一次或者零次，只是最接近的单元，如果用了其他正则分组，可以按分组判断
    path('register/', RegisterView.as_view(), name='register'),

    # 判断用户名是否存在
    path('checkName/', checkUsername, name='checkName'),
    path('checkEmail/', checkEmail, name='checkEmail'),

    # 用户登录
    path(r'login/', LoginView.as_view(), name='login'),

    # 用户退出
    path(r'logout/', LogoutView.as_view(), name='logout'),


    # 用户注册
    path('register/', RegisterView.as_view(), name='register'),


    # 用户信息
    path(r'profile/', UserProfileView.as_view(), name='profile'),

    # 用户密码
    path('password/', UserPasswordView.as_view(), name='password'),

    #重置密码
    path(r'resetPwd/', ResetPwdView.as_view(), name='resetPwd'),
    # 账户确认
    path(r'confirm/', ConfirmView.as_view(), name='confirm'),
    # 验证 验证码
    path('checkVerifyCode/', checkVerifyCode, name='checkVerifyCode'),
    # 上传头像
    path(r'uploadAvatar/', upload_avatar, name="uploadAvatar"),

    # 浏览历史
    path('history/', history, name='history'),
    path('history_del/', history_del, name='history_del'),

    # 我的订单
    path('order/', UserOrderView.as_view(), name='my_order'),

    # 支付宝同步通知
    path('order/return/', UserOrderReturnView.as_view(), name='order_return'),

    # 支付宝异步通知
    path('order/notify/', UserOrderNotifyView.as_view(), name='order_notify'),

    # 收货地址
    path('address/', AddressView.as_view(), name='address'),


    # 第三方快捷登录
    # QQ 登录
    path(r'qqLogin/', qq_login, name='qqLogin'),
    path(r'qqCallback/', qq_callback, name='qqCallback'),

    # github登录
    path(r'githubLogin/', github_login, name='githubLogin'),
    path(r'githubCallback/', github_callback, name='githubCallback'),
    # weibo登录
    path(r'weiboLogin/', weibo_login, name='weiboLogin'),
    path(r'weiboCallback/', weibo_callback, name='weiboCallback'),

    path(r'bindAccount/', bind_account, name='bindAccount'),
    path('bindLogin/', BindLoginView.as_view(), name='bindLogin'),
    path('bindSuccess/', bind_success, name='bindSuccess'),
]