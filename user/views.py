import os
import json
import urllib.parse
import uuid
import logging

from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Q
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django_redis import get_redis_connection
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger


import requests

from article.models import Article
from .models import Account, OAuthEx, AccountAddress
from shop.models import OrderInfo, OrderGoods
from .forms import LoginForm, RegisterForm, UpdateProfileForm, ChangePwdForm, ResetPwdPwdForm
from util import json_status

# Create your views here.
logger = logging.Logger('qmpython')

'''
使用authenticate()方法来认证一个给定的用户名(username)和密码(password)。该函数以关键字参数的形式接受认
证的凭证，默认配置的关键字是username和password。如果密码和用户名匹配，该函数返回一个User对象，否
则，该函数返回None.
默认只能使用用户名和密码登录，如果想过邮箱登录的话 需要重写authenticate方法
'''


class AccountBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 使用get需要注意: 如果查询的对象不存在的话，会抛出一个DoesNotExist的异常
            user = Account.objects.get(
                Q(username=username) | Q(email=username))  ##或查询，注意email是等于username，因为都是从表单username获取的值
            if user.check_password(password):  # 不类似用户名一样去查询密码，是因为密码存在数据库的时候是密文.可以使用check_password的方法
                return user
        except Exception as e:
            return None


'''
#如果这样返回，ajax还需要进行json解析
#views.py
return HttpResponse(json.dumps({"msg":"ok!"}))

#index.html
var data=json.parse(data)
console.log(data.msg);

--------------------
#如果这样返回，两边都不需要进行json的序列化与反序列化，ajax接受的直接是一个对象
#views.py
from django.http import JsonResponse
return JsonResponse({"msg":"ok!"})

#index.html
console.log(data.msg);

前端提供给后台的只能是字符串数据格式，后台返回给前台的就看返回的是什么数据格式，是字符串就必须解析之后再用。
'''
'''
先验证Django表单带的错误，然后再验证自定义，根据下面来验证
is_bound 是一个属性，它只验证数据字段存在不存在，不验证你的数据是否正确
print(register_form .is_bound)
模型表单的验证也是调用is_valid()方法或访问errors属性。
is_valid它会进行所有的验证，包括是否存在和是否正确,
使用cleaned_data 必须执行完is_valid 且返回为True才能获取数据,保存用户提交上来的数据
'''


# 注册
class RegisterView(View):
    def get(self, request):
        register_type = request.GET.get('register_type', '')
        nick_name = request.GET.get('nick_name', '')
        avatar_url = request.GET.get('avatar_url', '')
        signature = request.GET.get('signature', '')
        sex = request.GET.get('sex', '')
        open_id = request.GET.get('open_id', '')
        login_type = request.GET.get('login_type', '')

        context = {'register_type': register_type,
                   'open_id': open_id,
                   'nick_name': nick_name,
                   'avatar_url': avatar_url,
                   'sex': sex,
                   'signature': signature,
                   'login_type': login_type}

        return render(request, 'user/register.html', context=context)

    def post(self, request):
        json_data = request.body
        if not json_data:
            return json_status.params_error(message="参数错误")

        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf-8'))

        register_form = RegisterForm(dict_data)
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            email = register_form.cleaned_data['email']
            password = register_form.cleaned_data['password']

            # 密码进行加密存储
            # password = make_password(password)

            # 利用字典解包方式
            params = {'username': username, 'password': password, 'email': email}
            user = Account.objects.create_user(**params)

            # 如果是第三方关联新账户则还要新建第三方账户
            register_type = dict_data.get('register_type', '')
            nick_name = dict_data.get('nick_name', '')
            avatar_url = dict_data.get('avatar_url', '')
            sex = dict_data.get('sex', '')
            signature = dict_data.get('signature', '')
            open_id = dict_data.get('open_id', '')
            login_type = dict_data.get('login_type', '')

            if register_type == 'bind':
                user.nick_name = '{0}_{1}'.format(nick_name, user.id)  # 防止昵称重复
                user.avatar = avatar_url
                user.sex = sex
                user.profile = signature

                user.save(update_fields=['nick_name', 'avatar', 'sex', 'profile'])
                # print(user)

                OAuthEx.objects.create(user=user, openid=open_id, loginType=login_type)

            # Account.objects.create(**params) # 如果要Auth自带的User模型创建新对象，需要使用create_user方法，而不是create方法，自动会给密码加Hash。
            # Account.objects.create(username=username, password=password, email=email, is_active=False)
            # 如果使用实例化对象方式，一定要记住save保存到数据库中去；
            # user = Account(username = username,password=password,email=email,is_active=False)
            # user.save()

            login(request, user)
            return json_status.result(message=u'注册成功')

        return json_status.params_error(message=register_form.get_error())


# 判断用户名是否存在
def checkUsername(request):
    username = request.GET.get('username', None)

    if Account.objects.filter(username=username).exists():
        return json_status.params_error(message='该用户名已注册，请重新输入！')

    return json_status.result(message="该用户名可以使用")


# 判断邮箱是否存在
def checkEmail(request):
    email = request.GET.get('email', None)

    if Account.objects.filter(email=email).exists():
        return json_status.params_error(message='该邮箱已注册，请重新输入！')

    return json_status.result(message="该邮箱可以使用")


class LoginView(View):
    def get(self, request):
        return render(request, 'user/login.html')

    def post(self, request):
        json_data = request.body
        if not json_data:
            return json_status.params_error(message="参数错误")

        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf-8'))

        login_form = LoginForm(dict_data)
        if login_form.is_valid() and login_form.check_data():
            username = login_form.cleaned_data['username']  # cleaned_data必须是通过is_valid 验证后才能获取
            password = login_form.cleaned_data['password']
            remember = login_form.cleaned_data['remember']

            user = authenticate(username=username, password=password)  ##验证，调用自定义的authenticate
            if user:
                if user.is_active:
                    login(request, user)  # 登录，向session中添加SESSION_KEY, 便于对用户进行跟踪
                    # 如果调用login方法以后，
                    # request对象就会激活user属性，这个属性不管登录或者未登录都是存在

                    # 获取登录后所要跳转的地址
                    # 默认跳转到首页
                    # next_url = request.GET.get('next', reverse('index'))
                    # # 跳转到next_url
                    # response = redirect(next_url)

                    if remember:
                        # 默认值就是2周14天，单位秒
                        request.session.set_expiry(None)
                    else:
                        # 0表示默认值 浏览器关闭了就没了
                        request.session.set_expiry(0)

                    return json_status.result(message="登录成功")
                else:
                    message = '该用户还未激活！'
            else:
                message = '用户名或密码错误'

            return json_status.params_error(message=message)

        return json_status.params_error(message=login_form.get_error())


class LogoutView(View):
    def get(self, request):
        logout(request)  # 当执行完logout，实际就是清除了session中的user信息
        # 它接受一个HttpRequest对象并且没有返回值,所以，因为没有返回值，需要返回一个页面。
        # return render(request, 'login.html')
        next_url = request.GET.get('next', '')
        if next_url:
            return redirect(next_url)
        else:
            return redirect(reverse('index'))  # 重定向，url栏目地址跳转


# 用户信息
class UserProfileView(LoginRequiredMixin, View):  # 登录验证,主要用于比如说直接输入地址情况。
    # 如果需要指定单独的跳转，则该类中指定login_url属性
    # 如果需要指定全局的，则在settings中指定LOGIN_URL属性
    # login_url = '/account/login/'  # 没有登录则指定跳转
    def get(self, request):
        return render(request, 'user/my_profile.html')

    def put(self, request):  # 不像request.POST，是没有request.PUI的，需要用QueryDict(request.body)
        # print(request.body) #b'nick_name=test&email=&mobile_no=&qq=&birthday=&profile='
        # print(QueryDict(request.body)) #<QueryDict: {'mobile_no': [''], 'email': [''], 'profile': [''], 'nick_name': ['test'], 'qq': [''], 'birthday': ['']}>
        json_data = request.body
        if not json_data:
            return json_status.params_error(message='参数传递错误')

        dict_data = json.loads(json_data.decode('utf-8'))

        profile_form = UpdateProfileForm(dict_data)

        if profile_form.is_valid():
            nick_name = profile_form.cleaned_data['nick_name']
            sex = profile_form.cleaned_data['sex']
            mobile = profile_form.cleaned_data['mobile']
            qq = profile_form.cleaned_data['qq']
            birthday = profile_form.cleaned_data['birthday']
            profile = profile_form.cleaned_data['profile']
            _user = request.user

            is_exists = Account.objects.filter(~Q(id=_user.id), nick_name=nick_name).exists()
            if is_exists:
                message = '该昵称已存在！'
                return json_status.params_error(message=message)

            _user.nick_name = nick_name
            _user.sex = sex
            _user.mobile = mobile
            _user.qq = qq
            _user.birthday = birthday
            _user.profile = profile
            _user.save(update_fields=['nick_name', 'sex', 'mobile', 'qq', 'birthday', 'profile'])

            return json_status.result(message=u'更新资料成功', data={'nick_name': nick_name, 'sex': sex,
                                                               'mobile': mobile, 'qq': qq, 'birthday': birthday,
                                                               'profile': profile})

        return json_status.params_error(message=profile_form.get_error())


class UserPasswordView(View):
    def put(self, request):
        json_data = request.body
        if not json_data:
            return json_status.params_error(message='传递参数错误')

        dict_data = json.loads(json_data.decode('utf-8'))

        change_form = ChangePwdForm(dict_data)
        if change_form.is_valid():
            # 可以通过获取前端email值，也可以直接在这利用request直接获取，因为登录成功就激活了request的东西，session依然还在没注销就可以用了
            username = request.user.username
            password = change_form.cleaned_data['password']
            new_password = change_form.cleaned_data['new_password']

            # 验证输入的原密码是否正确，验证，调用自定义的authenticate
            user = authenticate(username=username, password=password)
            if user:
                user.set_password(new_password)
                user.save(update_fields=['password'])
                # 由于修改用户密码是在用户登录后进行的。但是当我完成这个功能后，发现密码一旦修改成功。
                # 在刷新的时候，会发现当前登录用户就变成空的了。这是由于密码修改后，原来的会话失效，
                # 可以重新到登录界面重新登录，这样可以解决这个问题，但是会影响用户体验。
                update_session_auth_hash(request, user)  # 更新session，因为原来的session存放的是旧密码
                return json_status.result(message='密码修改成功')
            else:
                return json_status.params_error(message='原密码输入错误!')

        return json_status.params_error(message=change_form.get_error())


class ResetPwdView(View):
    def get(self, request):
        return render(request, 'user/resetpwd.html')

    def post(self, request):
        reset_form = ResetPwdPwdForm(request.POST)

        if reset_form.is_valid():
            email = reset_form.cleaned_data['email']
            password = reset_form.cleaned_data['password']

            user = Account.objects.get(email=email)
            user.set_password(password)
            user.save()
            return json_status.result(message='重置密码成功')

        return json_status.params_error(message=reset_form.get_error())


class ConfirmView(View):
    def post(self, request):
        json_data = request.body
        if not json_data:
            return json_status.params_error(message='参数传递错误')

        dict_data = json.loads(json_data.decode('utf-8'))
        email = dict_data.get('email', '')
        if email.strip():
            # 用户是否存在
            if Account.objects.filter(email=email).exists():
                return json_status.result(data={'email': email})
            else:
                return json_status.params_error(message='该邮箱不存在！')

        return json_status.params_error(message='请输入您的邮箱！')


def checkVerifyCode(request):
    json_data = request.body
    if not json_data:
        return json_status.params_error(message='参数传递错误')

    dict_data = json.loads(json_data.decode('utf-8'))
    email = dict_data.get('email', '')
    verifyCode = dict_data.get('verifyCode', '')

    if len(verifyCode.strip()) == 0:
        return json_status.params_error(message='请输入邮箱收到的验证码！')

    # 缓存里面获取值，看是否有没有值
    conn_redis = get_redis_connection(alias='verify_code')
    # 创建保存邮箱验证码的标记key
    email_code_key = "email_code_key{}".format(email).encode('utf-8')
    real_email_code = conn_redis.get(email_code_key).decode('utf-8') if conn_redis.get(email_code_key) else None

    if not real_email_code or real_email_code != verifyCode.lower():
        return json_status.params_error(message='验证码错误或过期，请重新发送！')

    return json_status.result()


# 上传头像
def upload_avatar(request):
    # request.FILES (任何文件都会存在这里面 ) request.POST body(请求体)
    file = request.FILES.get('upload_avatar')
    # 文件名
    file_name = file.name
    # 文件保存
    # '/root/src/www/QmpythonBlog/media/avatar/'
    dir_path = settings.MEDIA_ROOT + '/avatar/'
    # '/root/src/www/QmpythonBlog/media/avatar/user_15.png'
    file_path = os.path.join(dir_path, file_name)

    with open(file_path, 'wb') as f:
        # file.chunks() 返回的是一个生成器 能被生成器 不会一次全部使用
        for chunk in file.chunks():
            f.write(chunk)
    # avatar/user_15.png

    # http://127.0.0.1:8000/account/uploadAvatar/  当前视图对应的绝对路径
    # print(request.build_absolute_uri())
    url_path = settings.MEDIA_URL + 'avatar/'  # '/media/avatar/'
    # 返回地址 http://127.0.0.1:8000 + url_path +file_name
    img_url = request.build_absolute_uri(url_path + file_name)  # 'http://www.qmpython.com:8000/media/avatar/user_15.png'

    request.user.avatar = img_url
    request.user.save(update_fields=['avatar'])

    return json_status.result(message="头像修改成功", data={'img_url': img_url})


# 浏览历史
@login_required
def history(request):
    #  建立redis连接
    conn_redis = get_redis_connection(alias='history')
    history_key = 'history_{}'.format(request.user.id)
    # # 获取用户最新浏览的前10篇文章
    # article_ids = conn_redis.lrange(history_key, 0, 9)
    # print(article_ids)
    # # # 从数据库中查询文章的具体信息
    # # articles = Article.objects.filter(id__in=article_ids) # 这样查出来的会没有浏览顺序
    # # 遍历获取用户浏览的文章信息,这样顺序会按照浏览历史排列
    # article_list = []
    # for id in article_ids:
    #     article = Article.objects.get(id=id)
    #     article_list.append(article)

    # {'文章id': 文章数量}, 获取history_key对应hash的所有键值
    article_dict = conn_redis.hgetall(history_key)
    #print(article_dict) # {b'17': b'2019-05-20 00:51:55', b'16': b'2019-05-20 00:52:02', b'18': b'2019-05-20 00:51:50', b'10': b'2019-05-20 00:52:09'}

    # 遍历获取文章的信息
    article_list = []
    for article_id, read_time in article_dict.items():
        # print(article_id, read_time) # b'18' b'2019-05-19 11:25:38'
        # 根据文章id获取文章信息
        article = Article.objects.get(id=article_id.decode('utf-8'))
        # 动态给article对象增加一个属性read_time，保存浏览文章的时间
        article.read_time = read_time.decode('utf-8')  # 技巧！！
        # 添加
        article_list.append(article)

    # 按照列表对象中的time倒序
    article_list.sort(key=lambda article: article.read_time, reverse=True)

    # 组织上下文
    context = {
        'article_list': article_list
    }

    return render(request, 'user/my_history.html', context=context)

@login_required
def history_del(request):
    conn_redis = get_redis_connection(alias='history')
    history_key = 'history_{}'.format(request.user.id)
    history_count = conn_redis.hlen(history_key)
    if not history_count:
        json_status.params_error(message='没有浏览历史')

    json_data = request.body
    dict_data = json.loads(json_data.decode('utf-8'))
    article_id = dict_data.get('article_id', '')
    if article_id:
        # hdel(name,*keys)：将name对应的hash中指定key的键值对删除
        conn_redis.hdel(history_key, article_id)
    else:
        # delete(*name) 根据name删除redis中的任意数据类型
        conn_redis.delete(history_key)

    return json_status.result()



class UserOrderView(View):
    '''用户-订单中心'''
    def get(self, request):
        # 获取用户订单信息
        user = request.user

        orders = OrderInfo.objects.filter(user=user).order_by('-create_time')
        # 遍历获取订单商品的信息
        for order in orders:
            # 根据order查询商品订单信息
            order_skus = OrderGoods.objects.filter(order=order)

            # 遍历order_skus计算商品小计
            for order_sku in order_skus:
                # 计算小计
                amount = order_sku.count * order_sku.price
                # 动态给order_sku增加属性amount，保存订单商品小计
                order_sku.amount = amount

            # 动态给order增加属性，保存订单商品的信息
            order.order_skus = order_skus

        # 分页数据
        try:
            page = int(request.GET.get('page', 1))  # 获取页码
        except PageNotAnInteger:
            logger.error("当前页数错误:PageNotAnInteger")
            page = 1

        # 实例化分页对象，articles需要分页的对象，在中间传一个数字，表示每页显示多少个
        paginator = Paginator(orders, settings.ONE_PAGE_COUNT, request=request)
        try:
            orders_info = paginator.page(page)  # 获取当前页的数据
        except EmptyPage:
            # 若访问的页数大于实际页数，则返回最后一页数据
            logger.info("访问的页数大于总页数")
            orders_info = paginator.page(paginator.num_pages)


        context = {
            'obj_info': orders_info
        }


        return render(request, 'user/my_order.html', context=context)


#"GET /user/order/?charset=utf-8
# &out_trade_no=20190528165115590334601
# &method=alipay.trade.page.pay.return
# &total_amount=13.00
# &sign=FifH5OlOgrIFJdPSCRRs1zGz%2FUh%2BloMKW0Y%2BP97%2BsN4xdeYsWsfLvwFGjnrOyR7HpKwpN%2B3Ujret%2BAO%2BZ%2FmQzyyaGCvAMZhA6l3VqLLiB9UC7Vq6ZxPdixkSS9EITnrJaR9fJGnGvM1mjdosGTvwz%2FAlXFQ7vunbbGuBLZ0cJFiQSNdS1KBYZhEib2091Q31h5Ps4usiIpJ8lFOEFHRfRY%2BwEBiv4e01DyqaPQYXmgHjG32Y7WJIgRqrpkTNPGXVEDPm0iQznwkzraV47hKRkcfR3dzCuG1%2B27bc1I%2FtYbe5pVEmcXZFKLvj%2FYg8H7%2BIBgxDLbMoWrm1pw5ciz%2FQJA%3D%3D
# &trade_no=2019052822001459351000015123
# &auth_app_id=2016092900624781
# &version=1.0&app_id=2016092900624781
# &sign_type=RSA2&seller_id=2088102177822976
# &timestamp=2019-05-28+16%3A52%3A09 HTTP/1.1" 200 31391


'''
1、终端消费者在商家网站选择商品，下订单。

2、商家把支付信息，get到支付宝指定的链接。

3、终端消费者在支付宝的网站上操作付款。

4、付款成功后，支付宝post付款成功的信息到商家预先提供的地址。

5、支付宝在终端消费者付款成功后三秒后，通过get跳回商家指定的链接。

'''

from alipay import AliPay

# alipay 同步通知
class UserOrderReturnView(View):
    def get(self, request):

        # 初始化
        alipay = AliPay(
            appid="2016092900624781",  # 应用appid
            app_notify_url="http://www.qmpython.com:8000/user/order/notify/",  # 默认回调url
            app_private_key_path=os.path.join(settings.BASE_DIR, 'shop/payment/app_private_key.pem'),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'shop/payment/alipay_public_key.pem'),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False，沙箱环境为True
        )

        data = request.GET
        process_dict = data.dict()  # QueryDict转换为字典对象
        #print(process_dict)
        sign = process_dict.pop('sign')

        success = alipay.verify(process_dict, sign)
        if success:
            return redirect(reverse('user:my_order'))



# alipay 异步通知
@method_decorator(csrf_exempt, name='dispatch')
class UserOrderNotifyView(View):
    def post(self, request):

        # 初始化
        alipay = AliPay(
            appid="2016092900624781",  # 应用appid
            app_notify_url="http://www.qmpython.com:8000/user/order/notify/",  # 默认回调url 异步支付通知url
            app_private_key_path=os.path.join(settings.BASE_DIR, 'shop/payment/app_private_key.pem'),  # 应用私钥
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'shop/payment/alipay_public_key.pem'),  # 支付宝公钥
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False，沙箱环境为True
        )

        data = request.POST  # QueryDict
        processed_dict = {}
        for key, value in data.items():
            processed_dict[key] = value

        # sign 不能参与签名验证，需要pop弹出来并保存值给下面用
        sign = processed_dict.pop('sign', None) # 单独拿出sign字段

        order_id = processed_dict.get("out_trade_no")

        # print(signature, order_id)

        # 校验参数
        if not order_id:
            return json_status.params_error(message='无效的订单id')

        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          pay_method=2,
                                          order_status=1)

        except OrderInfo.DoesNotExist:
            return json_status.params_error(message='订单错误')

        #print(processed_dict)

        success = alipay.verify(processed_dict, sign)
        if success and processed_dict["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
            # 支付成功
            # 获取支付宝交易号
            trade_no = processed_dict.get('trade_no')
            # 更新订单状态
            order.trade_no = trade_no
            order.order_status = 4  # 待评价
            order.save(update_fields=['trade_no', 'order_status'])
            # 跳转到我的订单页面，异步不用跳转，服务器间的交互，不像页面跳转同步通知可以在页面上显示出来，这种交互方式是不可见的；
            # 想办法处理同步更新页面
            # 程序执行完后必须打印输出“success”（不包含引号）。如果商户反馈给支付宝的字符不是success这7个字符，
            # 支付宝服务器会不断重
            # 程序执行完成后，该页面不能执行页面跳转。如果执行页面跳转，支付宝会收不到success字符，
            # 会被支付宝服务器判定为该页面程序运行出现异常，而重发处理结果通知；
            # 特性https://docs.open.alipay.com/270/105902/
            #print("trade succeed")

            return HttpResponse("success")


        return HttpResponse("fail")




class AddressView(View):
    def get(self, request):

        addresses = AccountAddress.objects.get(user=request.user)

        return render(request, 'user/deliver_address.html')


    def post(self, request):
        '''地址添加'''
        receiver = request.POST.get('receiver')
        address = request.POST.get('address')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        is_default = request.POST.get('is_default')

        # 校验数据
        if not all(receiver, address, phone):
            return json_status.params_error(message='数据不完整')

        # 校验手机
        import re
        if re.match(r'1[3|4|5|7|8][0-9]{9}$', phone):
            return json_status.params_error(message='手机号码不正确')

        # 业务处理
        user = request.user
        try:
            address = AccountAddress.objects.get(user=user, is_default=True)
        except AccountAddress.DoesNotExist:
            address = None

        if address:
            is_default = False
        else:
            is_default = True

        # 添加地址
        AccountAddress.objects.create(user=user,
                                      receiver=receiver,
                                      address=address,
                                      zip_code=zip_code,
                                      phone=phone,
                                      is_default = is_default)

        return render(request, 'user/deliver_address.html')


# 第三方登录

# 关联本网站账号
# 与本网站相关账户关联，关联新建账户或者绑定本网站已存在网站
def bind_account(request):
    nick_name = request.GET.get('nick_name', '')
    avatar_url = request.GET.get('avatar_url', '')
    open_id = request.GET.get('open_id', '')
    signature = request.GET.get('signature', '')
    sex = request.GET.get('sex', '')
    login_type = request.GET.get('login_type', '')

    context = {
        'nick_name': nick_name,
        'avatar_url': avatar_url,
        'open_id': open_id,
        'signature': signature,
        'sex': sex,
        'login_type': login_type
    }
    return render(request, 'user/bindAccount.html', context=context)


class BindLoginView(View):
    def get(self, request):
        nick_name = request.GET.get('nick_name', '')
        avatar_url = request.GET.get('avatar_url', '')
        open_id = request.GET.get('open_id', '')
        login_type = request.GET.get('login_type', '')

        context = {
            'nick_name': nick_name,
            'avatar_url': avatar_url,
            'open_id': open_id,
            'login_type': login_type
        }

        return render(request, 'user/bindLogin.html', context=context)

    def post(self, request):
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        open_id = request.POST.get('open_id', '')
        login_type = request.POST.get('login_type', '')

        if username.strip() == 0 and password.strip() == 0:
            return json_status.params_error(message="请输入用户名/邮箱或密码")

        # 判断网站里面是否有该账户
        user = authenticate(username=username, password=password)  ##验证，调用自定义的authenticate

        if user:
            if user.is_active:
                OAuthEx.objects.create(user=user, openid=open_id, loginType=login_type)
                login(request, user)

                return json_status.result(message="账号关联成功",
                                          data={'user_nick_name': user.nick_name,
                                                'user_head_img': user.avatar
                                                })
        else:
            return json_status.params_error(message="该用户不存在，请关联新账号!")


def bind_success(request):
    nick_name = request.GET.get('nick_name', '')
    avatar_url = request.GET.get('avatar_url', '')
    user_nick_name = request.GET.get('user_nick_name', '')
    user_head_img = request.GET.get('user_head_img', '')

    context = {'nick_name': nick_name,
               'avatar_url': avatar_url,
               'user_nick_name': user_nick_name,
               'user_head_img': user_head_img
               }

    return render(request, 'user/bindSuccess.html', context=context)



class OAuthBase:
    def __init__(self, client_id, client_key, redirect_url, state):
        self.client_id = client_id
        self.client_key = client_key
        self.redirect_url = redirect_url
        self.state = state

    # 授权请求 请求用户授权Token，获取Authorization code
    def get_auth_url(self, url):

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_url,
            'response_type': 'code',
            'state': self.state
        }

        # urllib.parse.urlencode 方法，将字典里面所有的键值转化为query-string格式（key=value&key=value）,
        # 多个参数用&分离，并且将中文转码
        url = url.format(urllib.parse.urlencode(params))

        return url

    # 令牌请求  获取授权过的Access Token，通过Authorization Code获取Access Token
    def get_access_token(self, url):

        data = {'client_id': self.client_id,
                'client_secret': self.client_key,
                'redirect_uri': self.redirect_url
                }

        url = url.format(urllib.parse.urlencode(data))
        headers = {'Accept': 'application/json'}  # 设置接受json类型
        resp = requests.post(url, headers=headers, data=data)  # 根据code获取access_token

        if resp.status_code == 200:
            # result = urllib.parse.parse_qs(resp.json())  # 这个函数主要用于分析URL中query组件的参数，返回一个key-value对应的字典格式；
            result = resp.json()

            return result

    # 获取用户资料
    def get_user_info(self, url):
        resp = requests.get(url)
        if resp.status_code == 200:
            info = resp.json()
            return info

    def get_user_some_info(self, url):
        pass


class OAuth_GITHUB(OAuthBase):
    # 获取用户一些资料
    def get_user_some_info(self, url):
        info = self.get_user_info(url)
        nick_name = info.get('login', '')
        avatar_url = info.get('avatar_url', '')
        sex = info.get('gender', '')  # 性别，m：男、f：女、n：未知
        open_id = str(info.get('id'))
        signature = info.get('bio', '')

        if not sex:
            sex = 'n'

        if not signature:
            signature = '无个性签名'

        someInfo = {
            'nick_name': nick_name,
            'avatar_url': avatar_url,
            'open_id': open_id,
            'sex': sex,
            'signature': signature
        }

        return someInfo


# 用户被重定向以请求他们的GitHub身份
def github_login(request):

    # 通过request获取查询字符串，next记录从哪里跳转的
    next = request.GET.get('next', '')
    if not next:
        next = "/"

    github = OAuth_GITHUB(settings.GITHUB_CLIENT_ID,
                          settings.GITHUB_CLIENT_SECRET,
                          settings.GITHUB_CALLBACK_URL,
                          next
                          )

    url = 'https://github.com/login/oauth/authorize?scope=user:email&{0}'

    return redirect(github.get_auth_url(url))


# 用户被GitHub重定向回您的网站
def github_callback(request):
    code = request.GET.get('code')  # 要获取到的Authorization Code值
    state = request.GET.get('state')  # 为上述随机产生的字符串
    loginType = '3'

    github = OAuth_GITHUB(settings.GITHUB_CLIENT_ID,
                          settings.GITHUB_CLIENT_SECRET,
                          settings.GITHUB_CALLBACK_URL,
                          state
                          )

    url = 'https://github.com/login/oauth/access_token?code=' + code + '&state=' + state + '&{0}'
    # 获取access_token的值
    result = github.get_access_token(url)

    # 使用access_token获取用户信息
    params = {'access_token': result['access_token']}
    url = 'https://api.github.com/user?{0}'.format(urllib.parse.urlencode(params))

    # 获得github授权用户的个人信息
    someInfo = github.get_user_some_info(url)
    someInfo['login_type'] = loginType

    # 查询第三方账户是否关联本网站账号
    github = OAuthEx.objects.filter(openid=someInfo['open_id'], loginType=loginType)

    if github and github[0].user.is_active:  # 若已存在且激活状态，直接登录
        login(request, github[0].user)
        return redirect(state)
    else:  # 如果不存在，则关联新账号或关联已有账号
        return redirect('/user/bindAccount?{0}'.format(urllib.parse.urlencode(someInfo)))

    #return redirect(reverse('user:login'))


class OAuth_QQ(OAuthBase):
    def get_access_token(self, url):  # QQ 获取access token有点区别所以重写此方法

        params = {'client_id': self.client_id,
                  'client_secret': self.client_key,
                  'redirect_uri': self.redirect_url
                  }

        url = url.format(urllib.parse.urlencode(params))
        resp = requests.get(url, params=params)  # 根据code获取access_token

        if resp.status_code == 200:
            result = urllib.parse.parse_qs(resp.text)  # 这个函数主要用于分析URL中query组件的参数，返回一个key-value对应的字典格式；

            return result

    # 获取用户OpenID_OAuth2.0
    def get_open_id(self, url):
        resp = requests.get(url)
        if resp.status_code == 200:
            result = resp.text  # callback( {"client_id":"10sss8870","openid":"758F02ffadd4C38Bfff89792C0946CE"} );

            result_str = result[9:-3]  # {"client_id":"10sss8870","openid":"758F02ffadd4C38Bfff89792C0946CE"}

            result_json = json.loads(result_str)  # 将json格式数据转换为字典,JSON反序列化为Python对象
            self.openid = result_json['openid']

            return self.openid

    # 获取用户一些资料
    def get_user_some_info(self, url):
        info = self.get_user_info(url)
        nick_name = info.get('nickname', '')
        avatar_url = info.get('figureurl_qq_2', '')
        sex = info.get('gender', '')  # 性别，m：男、f：女、n：未知
        open_id = self.openid
        signature = info.get('desc', '')

        if sex == '男':
            sex = 'm'
        elif sex == '女':
            sex = 'f'
        else:
            sex = 'n'

        if not signature:
            signature = '无个性签名'

        someInfo = {'nick_name': nick_name,
                    'avatar_url': avatar_url,
                    'open_id': open_id,
                    'sex': sex,
                    'signature': signature
                    }

        return someInfo


def qq_login(request):

    # 通过request获取查询字符串，next记录从哪里跳转的
    next = request.GET.get('next', '')
    if not next:
        next = "/"

    qq = OAuth_QQ(settings.QQ_APP_ID,
                  settings.QQ_APP_KEY,
                  settings.QQ_CALLBACK_URL,
                  next)

    qq_url = 'https://graph.qq.com/oauth2.0/show?which=Login&display=pc&scope=get_user_info&{0}'

    return redirect(qq.get_auth_url(qq_url))


def qq_callback(request):
    code = request.GET.get('code', '')
    state = request.GET.get('state', '')  # 如果传递参数，会回传该参数。
    loginType = '1'

    qq = OAuth_QQ(settings.QQ_APP_ID,
                  settings.QQ_APP_KEY,
                  settings.QQ_CALLBACK_URL,
                  state)


    url = 'https://graph.qq.com/oauth2.0/token?grant_type=authorization_code&code=' + code + '&{0}'

    # 通过Authorization Code获取Access Token
    result = qq.get_access_token(url)
    access_token = result['access_token'][0]
    # 使用AccessToken来获取用户的OpenID
    params = {'access_token': access_token}
    url = 'https://graph.qq.com/oauth2.0/me?{0}'.format(urllib.parse.urlencode(params))

    openid = qq.get_open_id(url)
    # 获取用户信息
    params = {'access_token': access_token, 'oauth_consumer_key': qq.client_id, 'openid': openid}

    url = 'https://graph.qq.com/user/get_user_info?{0}'.format(urllib.parse.urlencode(params))
    someInfo = qq.get_user_some_info(url)
    someInfo['login_type'] = loginType

    # 查询第三方账户是否关联本网站账号
    qq = OAuthEx.objects.filter(openid=openid, loginType=loginType)

    if qq and qq[0].user.is_active:  # 若已存在且激活状态，直接登录
        login(request, qq[0].user)
        return redirect(state)
    else:  # 如果不存在，则关联新账号或关联已有账号
        return redirect('/user/bindAccount?{0}'.format(urllib.parse.urlencode(someInfo)))

    #return redirect(reverse('user:login'))


class OAuth_WEIBO(OAuthBase):
    # 获取用户一些资料
    def get_user_some_info(self, url):
        info = self.get_user_info(url)
        nick_name = info.get('screen_name', '')
        avatar_url = info.get('avatar_hd', '')  # avatar_large  avatar_hd
        open_id = info.get('idstr', '')
        sex = info.get('gender', '')  # 性别，m：男、f：女、n：未知
        signature = info.get('description', '')

        if not sex:
            sex = 'n'

        if not signature:
            signature = '无个性签名'

        someInfo = {'nick_name': nick_name,
                    'avatar_url': avatar_url,
                    'open_id': open_id,
                    'sex': sex,
                    'signature': signature
                    }

        return someInfo


# weibo
def weibo_login(request):

    # 通过request获取查询字符串，next记录从哪里跳转的
    next = request.GET.get('next', '')
    if not next:
        next = "/"

    weibo = OAuth_WEIBO(settings.WEIBO_APP_KEY,
                        settings.WEIBO_APP_SECRET,
                        settings.WEIBO_CALLBACK_URL,
                        next)
    url = 'https://api.weibo.com/oauth2/authorize?scope=email&forcelogin=true&{0}'

    return redirect(weibo.get_auth_url(url))


def weibo_callback(request):
    code = request.GET.get('code', '')
    state = request.GET.get('state', '')  # 如果传递参数，会回传该参数。
    loginType = '2'

    weibo = OAuth_WEIBO(settings.WEIBO_APP_KEY,
                        settings.WEIBO_APP_SECRET,
                        settings.WEIBO_CALLBACK_URL,
                        '1234@qqcom')

    url = 'https://api.weibo.com/oauth2/access_token?grant_type=authorization_code&code=' + code + '&{0}'

    result = weibo.get_access_token(url)

    # 使用access_token获取用户信息
    params = {'access_token': result['access_token'], 'uid': result['uid']}
    url = 'https://api.weibo.com/2/users/show.json?{0}'.format(urllib.parse.urlencode(params))
    # 获得github授权用户的个人信息
    someInfo = weibo.get_user_some_info(url)
    someInfo['login_type'] = loginType

    # 查询第三方账户是否关联本网站账号
    weibo = OAuthEx.objects.filter(openid=someInfo['open_id'], loginType=loginType)

    if weibo and weibo[0].user.is_active:  # 若已存在且激活状态，直接登录
        login(request, weibo[0].user)
        return redirect(state)
    else:  # 如果不存在，则关联新账号或关联已有账号
        return redirect('/user/bindAccount?{0}'.format(urllib.parse.urlencode(someInfo)))

    #return redirect(reverse('user:login'))
