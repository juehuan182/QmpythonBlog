from django import forms
from django_redis import get_redis_connection

from util.forms import FormMixin
from article.models import Account


# 注册表单
class RegisterForm(forms.Form, FormMixin):
    # label 属性是form表单中特有的属性，代表这个字段的描述，这个字典类似于verbose_name
    username = forms.CharField(label=u'用户名', min_length=3, max_length=18,
                               error_messages={'required': u'用户名不能为空', 'min_length': u'用户名不少于3位',
                                               'max_length': u'用户名不超过18位'})
    email = forms.EmailField(label=u'邮箱', required=True, error_messages={'required': u'邮箱不能为空',
                                                                         'invalid': u'邮箱格式错误'})  # required 请求能否为空，True不能为空，默认为True
    # 存储到数据库的密码，是一个加密后的字符串，但是这里是通过前端传输过来的，并没进行加密
    password = forms.CharField(label=u'密码', required=True, min_length=6, max_length=16,
                               error_messages={'required': u'密码不能为空', 'min_length': u'密码不少于6位',
                                               'max_length': u'密码不超过16位'})

    email_code_text = forms.CharField(label=u'验证码', required=True, min_length=6, max_length=6,
                                 error_messages={'required': u'请输入邮箱收到的验证码', 'min_length': u'注册验证码为6位',
                                                 'max_length': u'注册验证码为6位'})

    # 表单自定义错误消息：重写方法clean_field（field是一个属性名），可以自定义针对某一个field的验证机制，一个属性一个对应方法
    # # clean() 或者 clean_xxx() 会在执行 form.is_valid() 的过程中被调用
    def clean_username(self):
        username = self.cleaned_data['username']
        if Account.objects.filter(username=username).exists():
            self.add_error('username', '该用户名已使用，请重新选择！')

        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if Account.objects.filter(email=email).exists():
            self.add_error('email', u'该邮箱已被注册，请使用其他邮箱')
        return email


    def clean_email_code_text(self):
        email = self.cleaned_data['email']
        email_code_text = self.cleaned_data['email_code_text']

        # 缓存里面获取值，看是否有没有值
        conn_redis = get_redis_connection(alias='verify_code')

        # 创建保存邮箱验证码的标记key
        email_code_key = "email_code_key{}".format(email).encode('utf-8')
        real_email_code = conn_redis.get(email_code_key).decode('utf-8') if conn_redis.get(email_code_key) else None

        if not real_email_code or real_email_code!=email_code_text.lower():
            return self.add_error('email_code_text', '验证码错误或过期，请重新发送！')

        return email_code_text


# 如果只是单个错误，使用raise ValidationError，否则这里raise抛出去了，后面就不能执行了
# 如果这里判断有多个错误存在，则使用add_error方法


# 登录表单
class LoginForm(forms.Form, FormMixin):
    username = forms.CharField(min_length=3, max_length=18, label='用户名',
                               error_messages={'required': '用户名或邮箱不能为空'})

    password = forms.CharField(min_length=6, max_length=16, label=u'密码',
                               error_messages={'required': u'密码不能为空', 'min_length': u'密码不少于6位',
                                               'max_length': u'密码不超过16位'})

    # image_code_text = forms.CharField(min_length=4, max_length=4, label=u'验证码',
    #                                 error_messages={'required': u'验证码不能为空', 'min_length': u'验证码不少于4位',
    #                                                 'max_length': u'验证码不超过4位'})
    # image_code_uuid = forms.UUIDField(error_messages={"required": "图片UUID不能为空"})
    image_code_uuid = forms.UUIDField(required=False)
    image_code_text = forms.CharField(required=False)


    remember = forms.BooleanField(required=False)  # 不验证

    # 自定义方法，验证码
    def check_data(self):
        image_code_uuid = self.cleaned_data['image_code_uuid']
        image_code_text = self.cleaned_data['image_code_text']

        if image_code_uuid:  # 如果有验证码UUID，则需要输入验证码且长度满足
            if not image_code_text:
                return self.add_error('image_code_text', '请输入验证码')

            if  len(image_code_text) != 4:
                return self.add_error('image_code_text', '验证码长度为4位')

            # 连接redis
            conn_redis = get_redis_connection(alias='verify_code')
            # 创建验证码key
            image_key = 'image_key_{}'.format(image_code_uuid).encode('utf-8') #reids是以bytes存储的所以需要编码

            # 取出图片验证码
            real_image_code_origin = conn_redis.get(image_key)

            #  三目运算，为空的不能解码，所以需要判断下
            real_image_code = real_image_code_origin.decode('utf-8') if real_image_code_origin else None

            # print(real_image_code)

            if not real_image_code or real_image_code != image_code_text.lower():
                return self.add_error('image_code_text', '验证码错误')

            conn_redis.delete(image_key)  # 如果存在则删除

        # 返回true没有这一步 验证不能通过
        return True



# 个人信息修改
class UpdateProfileForm(forms.Form, FormMixin):
    nick_name = forms.CharField(label=u'昵称', min_length=3, max_length=16,
                                error_messages={'required': u'昵称不能为空', 'min_length': u'昵称不少于3位',
                                                'max_length': u'昵称不超过16位'})
    sex = forms.CharField(label=u'性别', max_length=1, required=False, error_messages={
        'max_length': u'性别长度不超过1位'})  # required=False只是判断该字段是否必填项，其余的error_messages还是会校验的
    mobile = forms.CharField(label=u'手机', max_length=11, required=False,
                                error_messages={'max_length': u'手机号码不超过11位'})
    qq = forms.CharField(label=u'QQ', max_length=15, required=False, error_messages={'max_length': u'QQ长度不超过15位'})
    birthday = forms.DateField(label=u'生日', required=False)
    profile = forms.CharField(label=u'个人简介', max_length=400, required=False,
                              error_messages={'max_length': u'个人简介长度不超过400位'})


# 修改密码
class ChangePwdForm(forms.Form, FormMixin):
    password = forms.CharField(label=u'密码', min_length=6, max_length=16,
                               error_messages={'required': u'密码不能为空', 'min_length': u'密码不少于6位',
                                               'max_length': u'密码不超过16位'})
    new_password = forms.CharField(label=u'新密码', min_length=6, max_length=16,
                                   error_messages={'required': u'密码不能为空', 'min_length': u'密码不少于6位',
                                                   'max_length': u'密码不超过16位'})
    confirm_password = forms.CharField(label=u'确认密码', min_length=6, max_length=16,
                                       error_messages={'required': u'密码不能为空', 'min_length': u'密码不少于6位',
                                                       'max_length': u'密码不超过16位'})


    def clean_confirm_password(self):
        new_password = self.cleaned_data['new_password']
        confirm_password = self.cleaned_data['confirm_password']

        if new_password != confirm_password:
            self.add_error('confirm_password', '新密码和确认密码不一致！')

        return confirm_password


# 重置密码
class ResetPwdPwdForm(forms.Form, FormMixin):
    password = forms.CharField(label=u'新密码', min_length=6, max_length=16,
                               error_messages={'required': u'新密码不能为空', 'min_length': u'密码不少于6位',
                                               'max_length': u'密码不超过16位'})
    surePassword = forms.CharField(label=u'确认密码', min_length=6, max_length=16,
                                   error_messages={'required': u'确认密码不能为空', 'min_length': u'密码不少于6位',
                                                   'max_length': u'密码不超过16位'})
    email = forms.EmailField(label=u'邮箱', required=True, error_messages={'required': u'邮箱不能为空',
                                                                         'invalid': u'邮箱格式错误'})  # required 请求能否为空，True不能为空，默认为True

    def clean_surePassword(self):
        password = self.cleaned_data['password']
        surePassword = self.cleaned_data['surePassword']

        if password != surePassword:
            self.add_error('new_password2', '两次输入密码不一致')
        return password

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = Account.objects.get(email=email)
        except:
            self.add_error('email', '该邮箱不存在')
        return email


