import json
from datetime import datetime, timedelta
import logging
from collections import OrderedDict  # 创建有序字典

from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse
from django.shortcuts import render, Http404, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.utils.decorators import method_decorator

from django.db.models import Count
# from django.conf import settings

from QmpythonBlog import settings


#  权限相关
from django.contrib.auth.models import Group, Permission


from qiniu import Auth

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from urllib.parse import urlencode

from util.fastdfs.fdfs import FDFS_Client

from article.models import Column, Category, Tag, Article, ArticleRecommend, Advertising, Comment
from user.models import Account, FriendLink
from doc.models import Doc
from util import json_status

from .forms import ArticleAddForm, AdvertisingAddForm, DocPubForm

# Create your views here.


logger = logging.getLogger('qmpythonLog')

@login_required
def index(request):
    """
        登录验证；
        login_url = "/user/login/"
        如果没有登录成功，则跳转至内部定义的login_url，否则会跳转到`settings.LOGIN_URL`指定的URL中。即先找内部再找外部
        注意登录验证是用于一些只有登录了才能看的到的页面，但是可能存在一些直接输入url也可以看到这个页面，比如爬虫，
        只不过没对应值而已，这样是不安全的，所以在进入这些页面前需要进行验证，以避免直接输入url的情况，
        如果验证已经登录成功的则进入对应页面，没有则通过使用LoginRequiredMixin(基于类视图)或login_required(基于函数视图)相同的行为，
    """
    return render(request, 'admin/index.html')


'''
Django之CBV装饰器method_decorator
1.在类上添加:
    @method_decorator(wrapper,name='dispatch')需要带上dispatch
2.在类中某个方法上添加:
  @method_decorator(wrapper)
  参考：https://www.jb51.net/article/145465.htm
'''
# 注意：permissions除了用string指定单个权限之外，还支持list以及tuple用于多个权限。
# <app_label>.<permission_codename>

# @method_decorator(permission_required('article.add_column'), name='dispatch') 针对类视图全部方法
class ColumnManageView(LoginRequiredMixin, View):
    def get(self, request):
        """
            相当于sql:
                select t.id, t1.num_articles from `column` t,
                ( select column_id, COUNT(*) num_articles from category GROUP BY column_id ) t1

                where t.id = t1.column_id

        """
        columns = Column.objects.annotate(num_categories=Count('categories'))  # categories为模型类中设置的relate_name,否则为子表小写表名
        return render(request, 'admin/article/column_manage.html', locals())

    def post(self, request):
        if not request.user.has_perms('article.add_column'):   # 代码用通过has_perms进行权限判断，但是这个方式请求已经进入了我们的视图
            return json_status.params_error(message="没有权限进行添加操作")

        json_data = request.body
        if not json_data:
            return json_status.params_error(message="参数错误")
        # 将json转dict
        dict_data = json.loads(json_data.decode('utf-8'))
        column_name = dict_data.get('column_name')
        if not column_name.strip():
            return json_status.params_error(message="栏目名称不能为空")
        if len(column_name) > 20:
            return json_status.params_error(message="栏目名称最长不超过20个字")

        if Column.objects.filter(name=column_name).exists():
            return json_status.params_error(message="该栏目名称已存在")

        column_link_url = dict_data.get('column_link_url', '#') # 如果没填则默认给'#'

        column_index = dict_data.get('column_index')
        if not column_index.strip():
            return json_status.params_error(message="栏目位置不能为空")

        Column.objects.create(name=column_name, link_url=column_link_url, index=column_index)

        return json_status.result(message="栏目创建成功")


def getColumnList(request):
    columns = Column.objects.values('id', 'name') # <QuerySet [{'id': 1, 'name': '首页'}, {'id': 2, 'name': 'python入门'}, {'id': 3, 'name': 'python web'}]>
    column_list = [column for column in columns] # 等同于list(columns)
    return json_status.result(data={'column_list': column_list})


class ColumnEditView(PermissionRequiredMixin, View):
    """
        权限验证，类似登录验证，针对直接通过url访问的，在用户没有相应权限时重定向到登录页或者抛出异常。
        没有则通过PermissionRequiredMixin来实现与permission_required
    """
    # 单个权限
    # permission_required = 'article.view_column'
    # 多个权限，要同时具有，且的关系,元祖或列表都可
    # 相当于全局的，只有满足了上面权限中的一个就可以进入下面的了，否则就跳转到setting配置的LOGIN_URL去了
    permission_required = ('article.change_column', 'article.delete_column')

    # 当LoginRequiredMixin或者PermissionRequiredMixin调用继承自AccessMixin的handle_no_permission方法时，
    # 如果raise_exception被设置为True，会抛出一个PermissionDenied的异常403状态，否则跳转到login_url。
    raise_exception = True
    permission_denied_message = "没有权限进行操作"

    # 如果需要返回json数据给ajax数据，重写handle_no_permission方法，返回对应错误
    # def handle_no_permission(self):
    #     if self.raise_exception:
    #         return json_status.params_error(message=self.permission_denied_message)

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return json_status.params_error(message=self.permission_denied_message)
        else:
            return super(ColumnEditView, self).handle_no_permission()

    def put(self, request, column_id):
        """
            Django对于PUT/DELETE请求并没有像POST/GET那样有一个字典结构。
            我们需要手动处理request.body获取参数：
        """
        # print(settings.CSRF_HEADER_NAME)
        json_data = request.body
        # print(json_data)
        if not json_data:
            return json_status.params_error(message="参数错误")
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf-8'))
        column_name = dict_data.get('column_name', '')

        if not column_name.strip():
            return json_status.params_error(message="栏目名称不能为空")
        if len(column_name) > 20:
            return json_status.params_error(message="栏目名称最长不超过20个字")

        column_link_url = dict_data.get('column_link_url', '')
        if not column_link_url.strip():
            return json_status.params_error(message="链接地址为空")

        column_index = dict_data.get('column_index')
        if not column_index.strip():
            return json_status.params_error(message="栏目位置不能为空")

        column = Column.objects.only('id').filter(id=column_id).first()
        if not column:
            return json_status.params_error(message="该栏目不存在")

        if Column.objects.filter(name=column_name, link_url=column_link_url, index= column_index).exists():
            return json_status.params_error(message="栏目名称和链接地址都未变化，请重新编辑")

        column.name = column_name
        column.link_url = column_link_url
        column.index = column_index
        column.save(update_fields=['name', 'link_url', 'index'])

        return json_status.result(message='栏目修改成成功')


    def delete(self, request, column_id):
        column = Column.objects.only('id').filter(id=column_id).first()
        if not column:
            return json_status.params_error(message='需要删除的栏目不存在')

        # 删除
        column.delete()
        return json_status.result()


class CategoryManageView(View):
    def get(self, request):
        categories = Category.objects.annotate(num_articles=Count('article'))
        return render(request, 'admin/article/category_manage.html', locals())


    def post(self, request):
        if not request.user.has_perms('article.add_category'):   # 代码用通过has_perms进行权限判断，但是这个方式请求已经进入了我们的视图
            return json_status.params_error(message="没有权限进行添加操作")

        json_data = request.body # b'column_name=%E5%85%B3%E4%BA%8E'
        if not json_data:
            return json_status.params_error(message='参数错误')

        # 将json转dict
        dict_data = json.loads(json_data.decode('utf-8'))
        category_name = dict_data.get('categoryName', '')
        column_id = int(dict_data.get('columnId', 0))

        if not category_name.strip():
            return json_status.params_error(message='分类名称不能为空')

        if not column_id:
            return json_status.params_error(message='请选择所属栏目')

        if Category.objects.filter(name=category_name).exists():
            return json_status.params_error(message='该分类名称已存在，请重新填写')

        Category.objects.create(name=category_name, column_id=column_id)
        return json_status.result()


class CategoryEditView(PermissionRequiredMixin, View):
    permission_required = ('article.change_category', 'article.delete_category')
    raise_exception = True
    permission_denied_message = "没有权限进行操作"

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return json_status.params_error(message=self.permission_denied_message)
        else:
            return super(CategoryEditView, self).handle_no_permission()

    def put(self, request, category_id):
        json_data = request.body
        if not json_data:
            return json_status.params_error(message="参数错误")

        dict_data = json.loads(json_data.decode('utf-8'))

        category_name = dict_data.get('categoryName', '')
        column_id = int(dict_data.get('columnId', 0))

        category = Category.objects.only('id').filter(id=category_id).first()
        if category:
            if not category_name.strip():
                return json_status.params_error(message="请输入分类名称")

            column = Column.objects.filter(id=column_id).values('name')

            if not column:
                return json_status.params_error(message="所属栏目不存在，请重新选择")

            if  Category.objects.only('id').filter(name=category_name, column_id=column_id).exists():
                return json_status.params_error(message="分类名称和所属栏目已存在,请不要重复输入")

            category.column_id = column_id
            category.name = category_name
            category.save(update_fields=['name','column_id'])
            column = list(column) # 序列化需要转换
            return json_status.result(data={'column':column})  #TypeError: <Column: 下载s2222222> is not JSON serializable
        else:
            return json_status.params_error(message="需要修改的分类不存在")


    def delete(self, request, category_id):
        category = Category.objects.only('id').filter(id=category_id).first()

        if category:
            #  物理删除或者逻辑删除
            category.delete()
            return json_status.result(message='分类删除成功')
        else:
            return json_status.params_error(message='需要删除的分类不存在')

class TagManageView(View):
    def get(self, request):

        tags = Tag.objects.annotate(num_articles=Count('article'))

        return render(request, 'admin/article/tag_manage.html', locals())

    def post(self, request):
        if not request.user.has_perms('article.view_tag'):
            return json_status.params_error(message='没有添加操作权限')

        json_data = request.body  # b'column_name=%E5%85%B3%E4%BA%8E'
        if not json_data:
            return json_status.params_error(message="参数错误")

        # 将json转dict
        dict_data = json.loads(json_data.decode('utf-8'))

        tag_name = dict_data.get('tag_name')
        if tag_name and tag_name.strip():
            # 有就取这个数据，如果没有就创建数据,返回元组(<Column: 关于>, True)
            tag_tuple = Tag.objects.get_or_create(name=tag_name)
            tag_instance, tag_created_bolean = tag_tuple
            tag_dict = {
                "id": tag_instance.id,
                "name": tag_instance.name
            }

            # 三目运算
            return json_status.result(data=tag_dict) if tag_created_bolean else json_status.params_error(
                message="标签名称已存在")

        else:
            return json_status.params_error(message="标签名称不能为空")


class TagEditView(PermissionRequiredMixin, View):
    permission_required = ('article.change_tag', 'article.delete_tag')
    raise_exception = True
    permission_denied_message = "没有权限进行操作"

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return json_status.params_error(message=self.permission_denied_message)
        else:
            return super(TagEditView, self).handle_no_permission()

    def put(self, request, tag_id):
        json_data = request.body
        if not json_data:
            return json_status.params_error(message="参数错误")

            # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf-8'))
        # print(dict_data) # {'column_name': 'python爬虫test'}
        tag_name = dict_data.get('tag_name', None)
        tag = Tag.objects.only('id').filter(id=tag_id).first()
        if tag:
            if tag_name and tag_name.strip():
                if Tag.objects.only('id').filter(name=tag_name).exists():
                    return json_status.params_error(message="该标签名称已经存在,请不要重复输入")

                tag.name = tag_name
                tag.save(update_fields=['name'])
                return json_status.result()

            return json_status.params_error(message="标签名称为空")

        return json_status.params_error(message="该标签不存在")


    def delete(self, request, tag_id):
        tag = Tag.objects.only('id').filter(id=tag_id).first()

        if tag:
            #  物理删除或者逻辑删除
            tag.delete()
            return json_status.result()
        else:
            return json_status.params_error(message='需要删除的标签不存在')



class ArticleManageView(View):
    def get(self, request):
        """
        1.获取文章
        :param request:
        :return:
        """
        categories = Category.objects.only('id', 'name')  # .filter(is_delete=False)
        articles = Article.objects.only('id', 'title', 'author__username', 'category__name', 'create_time'). \
            select_related('author', 'category')  # .filter(is_delete=False)


        # 通过时间进行过滤
        try:
            start_time = request.GET.get('start_time', '')
            end_time = request.GET.get('end_time', '')

            # print(start_time, end_time)  # 2019/02/01 2019/02/05
            # print(type(start_time))   # <class 'str'>

            # 把 2019/02/01 转成 datetime
            start_time = datetime.strptime(start_time, '%Y-%m-%d') if start_time else ''

            # 因后面需要去数据库查找时间范围，用到__range，不包含endtime，所以要加一天
            end_time = datetime.strptime(end_time, '%Y-%m-%d') if end_time else ''

            # print(start_time, end_time)  # 2019-02-01 00:00:00 2019-02-06 00:00:00
            # print(type(start_time))   # <class 'datetime.datetime'>

            # RuntimeWarning: DateTimeField Article.modified_time received a naive datetime (2019-02-01 00:00:00)
            # while time zone support is active.RuntimeWarning)

        except Exception as e:
            logger.info('用户输入的时间有误：\n{}'.format(e))
            start_time = end_time = ''

        # 去数据库过滤 过滤出新闻在 开始时间和结束时间 之间
        from django.utils.timezone import make_aware
        if start_time and not end_time:
            articles = articles.filter(update_time__lte=make_aware(start_time))

        if end_time and not start_time:
            articles = articles.filter(update_time__gte=make_aware(end_time))

        if start_time and end_time:
            # print(start_time, end_time + timedelta(days=1))  # 2019-02-04 00:00:00 2019-02-09 00:00:00
            # print(make_aware(start_time), make_aware(end_time + timedelta(days=1)))  #  2019-02-04 00:00:00+08:00 2019-02-09 00:00:00+08:00

            articles = articles.filter(update_time__range=(make_aware(start_time), make_aware(
                end_time + timedelta(days=1))))  # BETWEEN 2019-02-03 16:00:00 AND 2019-02-08 16:00:00

        # 通过title进行过滤
        title = request.GET.get('title', '')
        if title:
            articles = articles.filter(title__icontains=title)

        # 通过作者名进行过滤
        author_name = request.GET.get('author_name', '')
        if author_name:
            articles = articles.filter(author__username__icontains=author_name)

        # 通过分类id进行过滤
        category_id = int(request.GET.get('category_id', 0))
        if category_id:
            articles = articles.filter(category_id=category_id)

        # 获取第几页内容
        try:
            page = int(request.GET.get('page', 1))  # 获取页码
        except PageNotAnInteger:
            logger.error("当前页数错误:PageNotAnInteger")
            page = 1

        # 实例化分页对象，articles需要分页的对象，在中间传一个数字，表示每页显示多少个
        paginator = Paginator(articles, settings.ONE_PAGE_COUNT, request=request)

        try:
            articles_info = paginator.page(page)  # 获取当前页的数据
        except EmptyPage:
            # 若访问的页数大于实际页数，则返回最后一页数据
            logger.info("访问的页数大于总页数")
            articles_info = paginator.page(paginator.num_pages)

        context = {
            'articles_info': articles_info,
            'start_time': start_time,
            'end_time': end_time,
            'title': title,
            'author_name': author_name,
            'categories': categories,
            'category_id': category_id,
            'other_param': urlencode({
                'start_time': datetime.strftime(start_time, '%Y-%m-%d') if start_time else '',
                'end_time': datetime.strftime(end_time, '%Y-%m-%d') if end_time else '',
                'title': title,
                'author_name': author_name,
                'category_id': category_id
            })
        }

        return render(request, 'admin/article/article_manage.html', context=context)


@csrf_exempt
def markDownUploadImage(request):
    image_file = request.FILES.get('editormd-image-file')
    if not image_file:
        logger.info('从前端获取图片失败')
        '''
            注意：editor.md期望你上传图片的服务返回如下json格式的内容
            {
                success : 0 | 1, //0表示上传失败;1表示上传成功
                message : "提示的信息",
                url     : "图片地址" //上传成功时才返回
            }            
        '''
        return JsonResponse({'success': 0, 'message': '从前端获取图片失败'})

    if image_file.content_type not in ('image/jpeg', 'image/png', 'image/gif','image/png', 'image/bmp', 'image/webp'):
        return JsonResponse({'success': 0, 'message': '不能上传非图片文件'})

    try:
        image_ext_name = image_file.name.split('.')[-1]
    except Exception as e:
        logger.error('图片扩展名异常:{}'.format(e))
        image_ext_name = 'jpg'

    try:
        upload_res = FDFS_Client.upload_by_buffer(image_file.read(), file_ext_name=image_ext_name)
    except Exception as e:
        logger.error('图片上传出现异常：{}'.format(e))
        return JsonResponse({'success': 0, 'message': '图片上传异常'})
    else:
        if upload_res.get('Status') != 'Upload successed.':
            logger.info('图片上传到FastDFS服务器失败')
            return JsonResponse({'success': 0, 'message': '图片上传到服务器失败'})
        else:
            image_name = upload_res.get('Remote file_id')
            image_url = settings.FASTDFS_SERVER_DOMAIN + image_name
            return JsonResponse({'success': 1, 'message': '图片上传成功', 'url': image_url})


# 图片上传至FastDFS服务器功能实现
def uploadImageToServer(request):
    # request.FILES (任何文件都会存在这里面 )
    # print(request.FILES) # <MultiValueDict: {'image_file': [<InMemoryUploadedFile: head.png (image/png)>]}>

    image_file = request.FILES.get('image_file')
    # print(image_file) # head.png

    if not image_file:
        logger.info('从前端获取图片失败')
        return json_status.params_error(message='从前端获取图片失败')

    if image_file.content_type not in ('image/jpeg', 'image/png', 'image/gif', 'image/bmp'):
        return json_status.params_error(message='不能上传非图片文件')

    try:
        image_ext_name = image_file.name.split('.')[-1]
    except Exception as e:
        logger.info('图片扩展名异常:{}'.format(e))
        image_ext_name = 'jpg'

    try:
        upload_res = FDFS_Client.upload_by_buffer(image_file.read(), file_ext_name=image_ext_name)
    except Exception as e:
        logger.error('图片上传出现异常：{}'.format(e))
        return json_status.params_error(message='图片上传异常')
    else:  # 如果try里面的语句可以正常执行，那么就执行else里面的语句（相当于程序没有碰到致命性错误）
        if upload_res.get('Status') != 'Upload successed.':
            logger.info('图片上传到FastDFS服务器失败')
            return json_status.params_error(message='图片上传到服务器失败')
        else:
            image_name = upload_res.get('Remote file_id')
            image_url = settings.FASTDFS_SERVER_DOMAIN + image_name
            return json_status.result(data={'image_url': image_url}, message='图片上传成功')



# def upload_file(request):
#     # request.FILES (任何文件都会存在这里面 ) request.POST body(请求体)
#     file = request.FILES.get('upload_file')
#     # <class 'django.core.files.uploadedfile.InMemoryUploadedFile'>
#     # <class 'django.core.files.uploadedfile.TemporaryUploadedFile'>
#     # django 对于你上传图片大小 会选择对应的 对象来  图形小于 2.5m
#     # print('==========')
#     # print(file)  # 2018.png
#     # print(file.name)  # 2018.png
#     # print(type(file))
#     # print(type(file.name))
#     # print('==========')
#     # 文件名
#     file_name = file.name
#     # file_path 文件保存
#     # x/media/加密字符串.png
#     file_path = os.path.join(settings.MEDIA_ROOT, file_name)
#     with open(file_path, 'wb') as f:
#         # file.chunks() 返回的是一个生成器 能被生成器 不会一次全部使用
#         for chunk in file.chunks():
#             f.write(chunk)
#     # 返回地址  http://192.168.31.200:8000 /media/xxx + settings.MEDIA_URL+file_name
#     file_url = request.build_absolute_uri(settings.MEDIA_URL + file_name)
#     # http://192.168.31.200:8000/admin/upload-file/ 当前视图对应的绝对路径
#     print(request.build_absolute_uri())
#     # return JsonResponse({"file_url": file_url})
#     return json_status.result(data={"file_url": file_url})


# 1. 安装 pip install qiniu
def up_token(request):
    access_key = settings.QI_NIU_ACCESS_KEY
    secret_key = settings.QI_NIU_SECRET_KEY
    bucket_name = settings.QI_NIU_BUCKET_NAME
    # print(request)
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 3600为token过期时间，秒为单位。3600等于一小时
    token = q.upload_token(bucket_name)

    return JsonResponse({"uptoken": token})

def uploadFileToServer(request):
    # request.FILES (任何文件都会存在这里面 ) request.POST body(请求体)
    file = request.FILES.get('doc_file')
    if not file:
        logger.info('从前端获取文件失败')
        return json_status.params_error(message='从前端获取文件失败')

    if file.content_type not in ('application/octet-stream', 'application/pdf',
                                 'application/zip', 'text/plain', 'application/x-rar',
                                 'video/mp4'):

        return json_status.params_error(message='不能上传非文本文件')

    try:
        doc_ext_name = file.name.split('.')[-1]
    except Exception as e:
        logger.info('文件拓展名异常：{}'.format(e))
        doc_ext_name = 'pdf'

    try:
        upload_res = FDFS_Client.upload_by_buffer(file.read(), file_ext_name=doc_ext_name)
    except Exception as e:
        logger.error('文件上传出现异常：{}'.format(e))
        return json_status.params_error(message='文件上传异常')
    else:
        if upload_res.get('Status') != 'Upload successed.':
            logger.info('文件上传到FastDFS服务器失败')
            return json_status.params_error(message='文件上传到服务器失败')
        else:
            file_name = upload_res.get('Remote file_id')
            file_url = settings.FASTDFS_SERVER_DOMAIN + file_name
            return json_status.result(data={'file_url': file_url}, message='文件上传成功')


# @method_decorator(csrf_exempt, name='dispatch')
class ArticleAddView(PermissionRequiredMixin, View):
    permission_required = 'article.add_article'
    raise_exception = True
    permission_denied_message = '没有权限进行操作'

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return json_status.params_error(message=self.permission_denied_message)
        else:
            return super(ArticleAddView, self).handle_no_permission()

    def get(self, request):
        categories = Category.objects.only('id')  # .filter(is_delete=False)
        tags = Tag.objects.only('id')

        return render(request, 'admin/article/article_add.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return json_status.params_error(message="参数错误")
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf-8'))

        article_form = ArticleAddForm(dict_data)
        if article_form.is_valid():
            try:
                '''
                save()方法接受一个commit的参数，其值为True或者False。默认为True。
                如果你声明 save(commit=False)，那么它就会返回一个还未保存至数据库的对象，
                这样的话 你可以用这个对象添加一些额外的数据，然后在用save（）保存到数据库
                '''
                article_instance = article_form.save(commit=False)
                article_instance.author = request.user
                # article_instance.author_id = request.user.id  # 直接通过id也是可以的
                article_instance.save()  # 保存单表信息
                article_form.save_m2m()  # 保存关联多对多信息，commit=False时注意manytomany要写上
                # 上面这三句完成的是和上面 article_form.save() 一样的操作。拆开就可以自定制操作了

            except Exception as e:
                logger.info('创建错误：\n{}'.format(e))
                # print(e)
                return json_status.params_error(message=e)
            else:
                return json_status.result(message=u'文章创建成功')
        else:
            # print(article_form.get_error())
            return json_status.params_error(message=article_form.get_error())


class ArticleEditView(PermissionRequiredMixin, View):
    permission_required = ('article.add_article', 'article.change_article', 'article.delete_article')
    raise_exception = True
    permission_denied_message = '没有权限进行操作'

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return json_status.params_error(message=self.permission_denied_message)
        else:
            return super(ArticleEditView, self).handle_no_permission()

    def get(self, request, article_id):
        """
        获取待编辑的文章
        :param request:
        :return:
        """
        article = Article.objects.filter(id=article_id).only('id').first()
        tags = Tag.objects.only('id')

        if article:
            categories = Category.objects.only('id', 'name')  # .filter(is_delete=False)
            context = {
                        'categories': categories,
                        'tags': tags,
                        'article': article
                       }

            return render(request, 'admin/article/article_add.html', context=context)
        else:
            raise Http404('需要更新的文章不存在！')


    def delete(self, request, article_id):
        """
        :param request:
        :param article_id:
        :return:
        删除文章
        """
        article = Article.objects.only('id').filter(id=article_id).first()
        if article:
            article.is_delete = True
            article.save(update_fields=['is_delete'])
            article.delete()
            return json_status.result(message='文章删除成功')
        else:
            return json_status.params_error(message='需要删除的文章不存在')


    def put(self, request, article_id):
        """
        更新文章
        :param request:
        :param article_id:
        :return:
        """
        article = Article.objects.filter(id=article_id).first()
        if not article:
            return json_status.params_error(message='需要更新的文章不存在')

        json_data = request.body
        if not json_data:
            return json_status.params_error(message='参数错误')
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf-8'))
        # 修改表数据是，记得把instance信息也传进去，不然是新建数据，而不是对某行数据进行修改。
        article_form = ArticleAddForm(dict_data, instance=article)  # # 指定给谁做修改
        if article_form.is_valid():
            article_form.save()
            return json_status.result(message='文章更新成功')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in article_form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return json_status.params_error(message=err_msg_str)


class RecommendArticleManageView(View):
    def get(self, request):
        recommend_articles = ArticleRecommend.objects.only('id')
        return render(request, 'admin/article/recommend_article_manage.html', locals())


class RecommendArticleAddView(PermissionRequiredMixin, View):
    permission_required = ('article.add_articlerecommend', 'article.change_articlerecommend', 'article.delete_articlerecommend')
    raise_exception = True
    permission_denied_message = '没有权限进行操作'

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return json_status.params_error(message=self.permission_denied_message)
        else:
            return super(ArticleEditView, self).handle_no_permission()


    def get(self, request):
        categories = Category.objects.only('id', 'name').annotate(num_articles=Count('article')).order_by('-num_articles')
        priority = ArticleRecommend.PRI_CHOICES # ((1, '第一级'), (2, '第二级'), (3, '第三级'), (4, '第四级'), (5, '第五级'), (6, '第六级'))
        #print({k:v for k,v in priority}) # 字典推导式 {1: '第一级', 2: '第二级', 3: '第三级', 4: '第四级', 5: '第五级', 6: '第六级'}
        priority_dict = OrderedDict(priority) # OrderedDict([(1, '第一级'), (2, '第二级'), (3, '第三级'), (4, '第四级'), (5, '第五级'), (6, '第六级')])
        #print(priority_dict)

        return render(request, 'admin/article/recommand_article_add.html', locals())

    def post(self, request):
        if not request.user.has_perms('article.add_articlerecommend'):
            return json_status.params_error(message='没有操作权限')

        json_data = request.body
        if not json_data:
            return json_status.params_error(message='参数错误')

        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf-8'))

        try:
            article_id = int(dict_data.get('article_id'))
        except Exception as e:
            logger.info('文章id参数异常：\n{}'.format(e))
            return json_status.params_error(message='参数错误')

        if not Article.objects.filter(id=article_id).exists():
            return json_status.params_error(message='文章不存在')

        try:
            priority = int(dict_data.get('priority'))
            priority_list = [i for i, _ in ArticleRecommend.PRI_CHOICES]
            if priority not in priority_list:
                return json_status.params_error(message='推荐文章的优先级设置错误')
        except Exception as e:
            logger.info('推荐文章优先级异常：\n{}'.format(e))
            return json_status.params_error('推荐文章的优先级设置错误')

        # 创建推荐文章
        if ArticleRecommend.objects.filter(article_id=article_id).exists():
            return json_status.params_error(message='该文章已推荐')

        else:
            ArticleRecommend.objects.create(article_id=article_id, priority=priority)
            return json_status.result()


class RecommendArticleEditView(PermissionRequiredMixin, View):
    permission_required = ('article.change_articlerecommend', 'article.delete_articlerecommend')
    raise_exception = True
    permission_denied_message = '没有权限进行操作'

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return json_status.params_error(message=self.permission_denied_message)
        else:
            return super(RecommendArticleEditView, self).handle_no_permission()

    def put(self, request, recommendarticle_id):
        json_data = request.body
        if not json_data:
            return json_status.params_error(message='参数错误')
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf-8'))

        try:
            priority = int(dict_data.get('priority'))
            priority_list = [i for i, _ in ArticleRecommend.PRI_CHOICES]

            if priority not in priority_list:
                return json_status.params_error(message="推荐文章的优先级设置错误")
        except Exception as e:
            logger.info('推荐文章优先级异常：\n{}'.format(e))
            return json_status.params_error(message="推荐文章的优先级设置错误")

        recommendarticle = ArticleRecommend.objects.only('id').filter(id=recommendarticle_id).first()

        if not recommendarticle:
            return json_status.params_error(message="需要推荐的文章不存在")

        if recommendarticle.priority == priority:
            return json_status.params_error(message="推荐文章的优先级未改变")

        recommendarticle.priority = priority
        recommendarticle.save(update_fields=['priority'])

        return json_status.result(message="推荐文章更新成功")

    def delete(self, request, recommendarticle_id):
        recommendarticle = ArticleRecommend.objects.only('id').filter(id=recommendarticle_id).first()
        # print(recommendarticle) # ArticleRecommend object (13)
        if recommendarticle:
            recommendarticle.delete()
            return json_status.result(message="推荐文章删除成功")
        else:
            return json_status.params_error(message="推荐文章不存在")


class ArticlesByCategoryIdView(View):
    def get(self, request):
        category_id = request.GET.get('categoryId', '')
        if not category_id:
            return json_status.params_error(message='请选择分类')

        articles = Article.objects.values('id', 'title').filter(category_id=category_id)
        #print(articles)  <QuerySet [{'id': 10, 'title': '文章标题文章标题'}, {'id': 9, 'title': '文章标题'}]>
        articles_list = [article for article in articles]  # list(article)
        #print(articles_list) [{'title': '文章标题文章标题', 'id': 10}, {'title': '文章标题', 'id': 9}]

        return json_status.result(data={'article': articles_list})


class AdvertisingManageView(PermissionRequiredMixin, View):
    permission_required = ('article.view_advertising')
    raise_exception = True
    permission_denied_message = "没有权限进行操作"

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return json_status.params_error(message=self.permission_denied_message)
        else:
            return super(AdvertisingManageView, self).handle_no_permission() # 抛出异常，django.core.exceptions.PermissionDenied: 没有权限进行操作


    def get(self, request):
        advertising_list = Advertising.objects.only('id')

        return render(request, 'admin/webSite/Advertising_manage.html', locals())


class AdvertisingEditView(PermissionRequiredMixin, View):
    permission_required = ('article.change_advertising', 'article.delete_advertising')
    raise_exception = True
    permission_denied_message = "没有权限进行操作"

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return json_status.params_error(message=self.permission_denied_message)
        else:
            return super(AdvertisingEditView, self).handle_no_permission()


    def get(self,request, advertising_id):
        advertising = Advertising.objects.only('id').filter(id=advertising_id).first()
        position_dict = OrderedDict(Advertising.POSITION_CHOICES)
        if not advertising:
            return json_status.params_error(message='需要更新的广告不存在')

        return render(request, 'admin/webSite/Advertising_add.html', locals())
    
    def put(self,request, advertising_id):
        advertising = Advertising.objects.only('id').filter(id=advertising_id).first()
        if not advertising:
            return json_status.params_error(message='需要更新的广告不存在')

        json_data = request.body
        if not json_data:
            return json_status.params_error(message='参数错误')

        dict_data = json.loads(json_data.decode('utf-8'))

        advertising_form = AdvertisingAddForm(dict_data, instance=advertising)
        if advertising_form.is_valid():
            advertising_form.save()
            return json_status.result(message='修改成功')
        else:
            return json_status.params_error(message=advertising_form.get_error())

    def delete(self,request, advertising_id):
        advertising = Advertising.objects.only('id').filter(id=advertising_id).first()

        if advertising:
            advertising.delete()
            # advertising.is_delete = True
            # advertising.save(update_fields=['is_delete'])
            return json_status.result()

        return json_status.params_error(message='需要更新的广告不存在')


class AdvertisingAddView(PermissionRequiredMixin, View):
    permission_required = ('article.add_advertising')
    raise_exception = True
    permission_denied_message = "没有权限进行操作"

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return json_status.params_error(message=self.permission_denied_message)
        else:
            return super(AdvertisingAddView, self).handle_no_permission()

    def get(self, request):
        position_dict = OrderedDict(Advertising.POSITION_CHOICES)

        return render(request, 'admin/webSite/Advertising_add.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return json_status.params_error(message='参数错误')

        dict_data = json.loads(json_data.decode('utf-8'))
        advertising_form = AdvertisingAddForm(dict_data)

        if advertising_form.is_valid():
            advertising_form.save()
            return json_status.result()

        return json_status.params_error(message=advertising_form.get_error())


# 友情链接
class FriendlinkManageView(PermissionRequiredMixin, View):
    permission_required = ('user.view_friendlink', 'user.add_friendlink')
    raise_exception = True
    permission_denied_message = '无添加权限'

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return json_status.params_error(message=self.permission_denied_message)
        else:
            return super(FriendlinkManageView, self).handle_no_permission()

    def get(self, request):

        friend_links = FriendLink.objects.all()
        return render(request, 'admin/webSite/friend_link_manage.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return json_status.params_error(message="参数错误")
        # 将json转dict
        dict_data = json.loads(json_data.decode('utf-8'))
        friendlink_name = dict_data.get('friendlink_name')
        if not friendlink_name.strip():
            return json_status.params_error(message="名称不能为空")
        if len(friendlink_name) > 20:
            return json_status.params_error(message="名称最长不超过20个字")

        if FriendLink.objects.filter(name=friendlink_name).exists():
            return json_status.params_error(message="该名称已存在")

        friendlink_url = dict_data.get('friendlink_url') # 如果没填则默认给'#'
        if not friendlink_url.strip():
            return json_status.params_error(message="链接地址不能为空")

        FriendLink.objects.create(name=friendlink_name, link_url=friendlink_url)

        return json_status.result()


class FriendlinkEditView(PermissionRequiredMixin, View):
    permission_required = ('user.change_friendlink', 'user.delete_friendlink')
    raise_exception = True
    permission_denied_message = '无操作权限'

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return json_status.params_error(message=self.permission_denied_message)
        else:
            return super(FriendlinkEditView, self).handle_no_permission()

    def put(self, request, friendlink_id):
        json_data = request.body
        # print(json_data)
        if not json_data:
            return json_status.params_error(message="参数错误")
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf-8'))
        friendlink_name = dict_data.get('friendlink_name', '')

        if not friendlink_name.strip():
            return json_status.params_error(message="名称不能为空")
        if len(friendlink_name) > 20:
            return json_status.params_error(message="名称最长不超过20个字")

        friendlink_url = dict_data.get('friendlink_url', '')
        if not friendlink_url.strip():
            return json_status.params_error(message="链接地址为空")

        friendlink = FriendLink.objects.only('id').filter(id=friendlink_id).first()
        if not friendlink:
            return json_status.params_error(message="该友情链接不存在")

        if FriendLink.objects.filter(name=friendlink_name, link_url=friendlink).exists():
            return json_status.params_error(message="名称和链接地址都未变化，请重新编辑")

        friendlink.name = friendlink_name
        friendlink.link_url = friendlink_url
        friendlink.save(update_fields=['name', 'link_url'])

        return json_status.result()


    def delete(self, request, friendlink_id):
        friendlink = FriendLink.objects.only('id').filter(id=friendlink_id).first()
        if not friendlink:
            return json_status.params_error(message='需要删除不存在')
        # 删除
        friendlink.delete()
        return json_status.result()


class DocsManageView(View):
    @method_decorator(permission_required('doc.view_doc',login_url=None, raise_exception=True))
    def get(self, request):
         docs = Doc.objects.only('title', 'create_time').filter(is_delete=False)
         return render(request, 'admin/doc/docs_manage.html', locals())


class DocsEditView(PermissionRequiredMixin,View):
    permission_required = ('doc.change_doc', 'doc.delete_doc')
    raise_exception = True
    permission_denied_message = '无操作权限'

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return json_status.params_error(message=self.permission_denied_message)
        else:
            return super(DocsEditView, self).handle_no_permission()

    def get(self, request, doc_id):
        doc = Doc.objects.filter(id=doc_id, is_delete=False).first()
        return render(request, 'admin/doc/docs_pub.html', locals())

    def delete(self, request, doc_id):
        doc = Doc.objects.filter(id=doc_id,is_delete=False).filter()
        if not doc:
            return json_status.params_error(message='需要删除的文档不存在')
        # 逻辑删除
        # doc.is_delete = True
        # doc.save(update_fields=['is_delete'])
        # 物理删除
        doc.delete()
        return json_status.result()

    def put(self, request, doc_id):
        doc = Doc.objects.filter(id=doc_id, is_delete=False).first()
        if not doc:
            return json_status.params_error(message='需要更新的文档不存在')

        json_data = request.body
        if not json_data:
            return json_status.params_error(message='参数错误')
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf-8'))
        doc_form = DocPubForm(dict_data, instance=doc)
        if doc_form.is_valid():
            doc_form.save()
            return json_status.result()

        return json_status.params_error(message=doc_form.get_error())


@method_decorator(permission_required('doc.add_doc', raise_exception=True), name='dispatch')
class DocsPubView(View):
    def get(self, request):
        return render(request, 'admin/doc/docs_pub.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return json_status.params_error(message="参数错误")

        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf-8'))

        doc_form = DocPubForm(dict_data)
        if doc_form.is_valid():
            doc_instance = doc_form.save(commit=False)
            doc_instance.author = request.user
            doc_instance.save()
            return json_status.result()

        return json_status.params_error(message=doc_form.get_error())

class GroupManagerView(View):
    @method_decorator(permission_required('group.view_group', raise_exception=True))
    def get(self, request):
        groups = Group.objects.only('id').annotate(num_users=Count('user'))
        return render(request, 'admin/user/group_manage.html', {'groups': groups})


class GroupAddView(PermissionRequiredMixin, View):
    permission_required = 'group.add_group'
    raise_exception = True
    permission_denied_message = '无添加操作'

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return json_status.params_error(message=self.permission_denied_message)
        else:
            return super(GroupAddView, self).handle_no_permission()

    def get(self, request):
        permissions = Permission.objects.only('id')
        return render(request, 'admin/user/group_add.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            json_status.params_error(message='参数错误')

        dict_data = json.loads(json_data.decode('utf-8'))

        #   获取前端填写的角色名，进行判断
        group_name = dict_data.get('name', '').strip()
        if not group_name:
            return json_status.params_error(message='角色名不能为空')

        one_group, is_created = Group.objects.get_or_create(name=group_name)  # get_or_create适合于新增数据的时候
        if not is_created:
            return json_status.params_error(message='角色名已存在')

        group_permissions = dict_data.get('group_permissions')
        # print(group_permissions, type(group_permissions)) ['431', '432', '433'] list
        if not group_permissions:
            return json_status.params_error(message='没有分配权限')

        try:
            permissions_set = set(int(i) for i in group_permissions)    # 集合推导式, 无序、不重复
        except Exception as e:
            logger.info('传的权限参数异常：\n{}'.format(e))
            return json_status.params_error(message='权限参数异常')

        #   取出权限表里面的id，集合推导式
        all_permissions_set = set(i.id for i in Permission.objects.only('id'))
        #  issubset()方法用于判断集合的所有元素是否都包含在指定集合中，如果是则返回True，否则返回False。
        if not permissions_set.issubset(all_permissions_set):   #  判断传的参数是否在权限表范围内
            return json_status.params_error(message='有不存在的权限参数')

        #   设置权限
        for permission_id in permissions_set:
            p = Permission.objects.get(id=permission_id)
            one_group.permissions.add(p)   #  给组添加权限

        one_group.save()

        return json_status.result()

    '''    
    创建组并分配对应组的权限
    给组添加权限，涉及到组group表和permission权限表，以及中间关联表。其为ManyToManyFiled()关联关系，
    关联字段为permissions 语法:
        添加权限：group对象.permissions.add(permission对象1, permission对象2)
        删除权限：group对象.permissions.remove(permission对象1, permission对象2)
        清空权限：group对象.permissions.clear()       
    '''

class GroupEditView(PermissionRequiredMixin, View):
    permission_required = ('group.change_group', 'group.delete_group')
    raise_exception = True
    permission_denied_message = '无操作权限'

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return json_status.params_error(message=self.permission_denied_message)
        else:
            return super(GroupEditView, self).handle_no_permission()

    def get(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        permissions = Permission.objects.only('id')
        return render(request, 'admin/user/group_add.html', locals())

    def put(self, request, group_id):
        group = Group.objects.filter(id=group_id).first()
        if not group:
            raise Http404('需要修改的角色不存在！')

        json_data = request.body
        #print(json_data) #b'{"name":"\xe7\x94\xa8\xe6\x88\xb7\xe7\xbb\x843","group_permissions":["372","373","374","375","376","377","378","379"]}'
        if not json_data:
            return json_status.params_error(message='参数错误')
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf-8'))
        #print(dict_data) #{'name': '用户组3', 'group_permissions': ['372', '373', '374', '375', '376', '377', '378', '379']}

        # 取出组名，进行判断
        group_name = dict_data.get('name', '').strip()
        if not group_name:
            return json_status.params_error(message='角色名为空')

        # 取出权限
        group_permissions = dict_data.get('group_permissions')
        #print(group_permissions, type(group_permissions))  #    ['431', '432', '433'] <class 'list'>
        if not group_permissions:
            return json_status.params_error(message='权限参数为空')

        try:
            permissions_set = set(int(i) for i in group_permissions)
        except Exception as e:
            logger.info('传的权限参数异常：\n{}'.format(e))
            return json_status.params_error(message='权限参数异常')

        all_permissions_set = set(i.id for i in Permission.objects.only('id'))
        if not permissions_set.issubset(all_permissions_set):
            return json_status.params_error(message='有不存在的权限参数')

        #  获取该用户组具有的权限
        existed_permissions_set = set(i.id for i in group.permissions.all())
        #  如果前端传过来的组名和该组的组名一样并且前端传过来的权限和该组已有的一致，说明信息并没有修改
        if group_name == group.name and permissions_set == existed_permissions_set:
            return json_status.params_error(message='角色信息未修改')

        #1.先将原来的清空
        group.permissions.clear()

        #2.设置新的权限
        for permission_id in permissions_set:
            p = Permission.objects.get(id=permission_id)
            #2.加入新修改的
            group.permissions.add(p)

        group.name = group_name
        group.save()

        return json_status.result()

    def delete(self, request, group_id):
        group = Group.objects.filter(id=group_id).first()
        if not group:
            raise Http404('需要修改的角色不存在！')

        group.permissions.clear()  #  先清空对应用户组权限
        group.delete()   #  然后删除对应用户组

        return json_status.result()


@permission_required('group.view_group',raise_exception=True)
def viewGroup(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    permissions = Permission.objects.only('id')
    return render(request, 'admin/user/group_view.html', locals())


@method_decorator(permission_required(('user.view_account', 'group.view_group'),raise_exception=True), name='dispatch')
class UserGroupManageView(View):
    def get(self, request):
        users = Account.objects.only('id').filter(is_staff=True)
        user_list = [user for user in users if user.get_groups_name() or user.is_superuser] # 将分配了角色的用户取出来

        return render(request, 'admin/user/user_group_manage.html', locals())


class UserGroupEditView(PermissionRequiredMixin, View):
    permission_required = ('user.change_account', 'user.delete_account','group.change_group', 'group.delete_group')
    raise_exception = True
    permission_denied_message = '无操作权限'

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return json_status.params_error(message=self.permission_denied_message)
        else:
            return super(UserGroupEditView, self).handle_no_permission()

    def get(self, request, user_id):
        user_instance = Account.objects.filter(id=user_id).first()
        group_list = Group.objects.only('id')

        return render(request, 'admin/user/user_group_add.html', locals())

    def put(self, request, user_id):
        user_instance = Account.objects.filter(id=user_id).first()
        if not user_instance:
            return json_status.params_error(message="需要修改角色的用户不存在")

        json_data = request.body
        if not json_data:
            return json_status.params_error(message='参数错误')

        dict_data = json.loads(json_data.decode('utf-8'))

        groups_id = dict_data.get('groupIds')
        if not groups_id:
            return json_status.params_error(message='没有分配角色')

        try:
            groups_id_set = set(int(group_id) for group_id in groups_id)
        except Exception as e:
            logger.info('传的角色参数异常:\n{}'.format(e))
            return json_status.params_error(message='角色参数异常')

        # 取出角色表里面的id,集合推导式
        all_group_id_set = set(group.id for group in Group.objects.only('id'))
        # issubset()方法用于判断传的参数是否在权限表范围内
        if not groups_id_set.issubset(all_group_id_set):
            return json_status.params_error(message='有不存在的角色参数')

        groups = Group.objects.filter(id__in=groups_id_set)
        # 先清除组
        user_instance.groups.clear()
        user_instance.groups.set(groups)

        groupname_list = [group.name for group in groups]
        groups_name = '、'.join(groupname_list)

        data = {
            'username': user_instance.username,
            'groupsname': groups_name
        }

        return json_status.result(data=data)

    def delete(self, request, user_id):
        user_instance = Account.objects.filter(id=user_id).first()
        if not user_instance:
            return json_status.params_error(message="需要取消角色的用户不存在")

        user_instance.groups.clear()  #清除用户组（角色）
        user_instance.user_permissions.clear() #清除用户权限，可能用户还会单独分配了权限
        user_instance.is_staff = False  # 不允许登录后台管理系统
        user_instance.save()
        return json_status.result()


@method_decorator(permission_required(('user.add_account','group.add_group'), raise_exception=True), name='dispatch')
class UserGroupAddView(View):
    def get(self, request):
        group_list = Group.objects.only('id')
        return render(request, 'admin/user/user_group_add.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return json_status.params_error(message='参数错误')

        dict_data = json.loads(json_data.decode('utf-8'))

        user_id = int(dict_data.get('userId', 0))
        if not user_id:
            return json_status.params_error(message='请选择用户')

        groups_id = dict_data.get('groupIds')
        if not groups_id:
            return json_status.params_error(message='没有分配角色')

        try:
            groups_id_set = set(int(group_id) for group_id in groups_id)
        except Exception as e:
            logger.info('传的角色参数异常:\n{}'.format(e))
            return json_status.params_error(message='角色参数异常')

        # 取出角色表里面的id,集合推导式
        all_group_id_set = set(group.id for group in Group.objects.only('id'))
        # issubset()方法用于判断传的参数是否在权限表范围内
        if not groups_id_set.issubset(all_group_id_set):
            return json_status.params_error(message='有不存在的角色参数')

        user = Account.objects.filter(id=user_id).first()

        # 给用户分配组（角色）
        groupname_list = []
        for group_id in groups_id_set:
            group = Group.objects.get(id=group_id)
            groupname_list.append(group.name)
            user.groups.add(group)

        user.is_staff = True  # 设置可登陆后台管理
        user.save()

        groups_name = '、'.join(groupname_list)

        data = {
            'username': user.username,
            'groupsname': groups_name
        }

        return json_status.result(data=data)


def getGroupUser(request):
    json_data = request.body
    if not json_data:
        return json_status.params_error(message='参数错误')

    dict_data = json.loads(json_data.decode('utf-8'))

    username = dict_data.get('username')
    # 将QuerySet列表对象强制转换成list进行传送
    accounts = Account.objects.values('id', 'username').filter(username__icontains=username)
    if not accounts:
        return json_status.params_error(message='没有搜索到结果')

    account_list = [account for account in accounts] # 等同于list(accounts) [{'username': 'llp182', 'id': 2}]

    return json_status.result(data={'account_list': account_list})


@method_decorator(permission_required('user.view_account', raise_exception=True), name='dispatch')
class UserInfoView(View):
    def get(self,request):
        users = Account.objects.only('id','username','email','mobile','qq','sex','date_joined','is_active')
        user_id = request.GET.get('user_id', '') # GET方式数据一般不在请求体不能用request.body获取，否则为None，前端也不需要序列化

        # 通过客户ID过滤
        if user_id:
            users = users.filter(id=user_id)

        user_name = request.GET.get('user_name', '')
        # 通过用户名过滤
        if user_name:
            users = users.filter(username=user_name)

        user_email = request.GET.get('user_email', '')
        if user_email:
            users = users.filter(email=user_email)

        user_sex = request.GET.get('user_sex', '')
        if user_sex in(['m','f']):
            users = users.filter(sex=user_sex)

        # 进行分页

        # 获取第几页内容
        try:
            page = int(request.GET.get('page', 1))
        except PageNotAnInteger:
            logger.error('当前页数错误:PageNotAnInteger')
            page = 1

        # 实例化分页对象，users需要分页的对象，在中间传一个数字，表示每页显示多少个
        paginator = Paginator(users, settings.ONE_PAGE_COUNT, request=request)

        try:
            users_info = paginator.page(page)  # 获取当前页的数据
        except EmptyPage:
            # 若访问的页数大于实际页数，则返回最后一页数据
            logger.info('访问的页数大于总页数')
            users_info = paginator.page(paginator.num_pages)

        context = {
            'users_info': users_info,
            'user_id': user_id,
            'user_name': user_name,
            'user_email': user_email,
            'user_sex': user_sex,
            'other_param': urlencode({
                'user_id': user_id,
                'user_name': user_name,
                'user_email': user_email,
                'user_sex': user_sex
            })
        }

        return render(request, 'admin/user/user_info.html', context=context)



class UserInfoEditView(View):
    @method_decorator(permission_required('user.change_account', raise_exception=True))
    def put(self, request, user_id):
        user_instance = Account.objects.filter(id=user_id).first()
        if not user_instance:
            return json_status.params_error('用户不存在')

        json_data = request.body
        if not json_data:
            return json_status.params_error(message='参数错误')

        dict_data = json.loads(json_data.decode('utf-8'))
        is_active = int(dict_data.get('is_active'))  # '0' 表示要停用，'1'表示要启用
        if is_active:
            user_instance.is_active = True
        else:
            user_instance.is_active = False

        user_instance.save(update_fields=['is_active'])

        return json_status.result()


class CommentsManageView(View):
    @method_decorator(permission_required('article.view_comment', raise_exception=True))
    def get(self, request):
        comments = Comment.objects.annotate(children_nums=Count('comment'))
        return render(request, 'admin/article/comments_manage.html', locals())


class CommentsEditView(PermissionRequiredMixin, View):
    permission_required = ('article.change_comment', 'article.delete_comment')
    raise_exception = True
    permission_denied_message = '无操作权限'
    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return json_status.params_error(message=self.permission_denied_message)
        else:
            return super(CommentsEditView, self).handle_no_permission()

    def put(self, request, comment_id):
        comment = Comment.objects.filter(id=comment_id).first()
        if not comment:
            return json_status.params_error('该评论不存在')

        json_data = request.body
        if not json_data:
            return json_status.params_error(message='参数错误')

        dict_data = json.loads(json_data.decode('utf-8'))
        is_delete = int(dict_data.get('is_delete'))  # '0' 表示要停用，'1'表示要启用
        if is_delete: # 1要去开启
            comment.is_delete = False
        else:
            if comment.comment_set.all():
                return json_status.params_error(message='存在子评论不能禁用')
            else:
                comment.is_delete = True

        comment.save(update_fields=['is_delete'])

        return json_status.result()


    def delete(self, request, comment_id):
        comment = Comment.objects.filter(id=comment_id).first()
        if comment:
            if comment.comment_set.all():
                return json_status.params_error(message='存在子评论不能删除')
            else:
                comment.delete() # 物理删除
                return json_status.result()
        else:
            return json_status.params_error(message="该评论不存在")


# 违禁词
class ProhibitedWordsManageView(View):
    def get(self, request):
        # import os
        # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # path = os.path.join(BASE_DIR, 'util',"prohibited_words.txt")
        # # 查出所有违禁词
        # with open(path,'r') as f:
        #     prohibited_words_list = f.readlines()

        return render(request, 'admin/article/prohibitedWords_manage.html', locals())

    def post(self, request):
        # request.FILES (任何文件都会存在这里面 ) request.POST body(请求体)
        file = request.FILES.get('words_file')

        if not file:
            logger.info('从前端获取文件失败')
            return json_status.params_error(message='从前端获取文件失败')

        if file.content_type not in('text/plain'):
            return json_status.params_error(message='不能上传非txt文件')

        # 读写文件内容
        import os
        file_path = os.path.join(settings.BASE_DIR, 'util',"prohibited_words.txt")

        content_list = file.readlines()  # 一次读取所有，返回一个列表，列表的元素为文件行的内容。
        # print(content_list)

        with open(file_path, 'a') as f:
            for chunk in content_list:
                f.write(chunk.decode('gbk'))

        return json_status.result()


class RobotsManageView(View):
    def get(self, request):
        import os
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(BASE_DIR, 'templates', 'robots.txt')

        # 读取文件上次更新时间
        modify_timestamp = os.path.getmtime(file_path)
        # print(type(modify_timestamp))
        modify_time = datetime.fromtimestamp(modify_timestamp)
        # print(modify_time)  # 获取文件的修改时间

        return render(request, 'admin/webSite/robots_manage.html', locals())


    def post(self, request):
        json_data = request.body
        if not json_data:
            return json_status.params_error(message='参数错误')

        dict_data = json.loads(json_data.decode('utf-8'))
        robots = dict_data.get('robots_content')
        import os
        file_path = os.path.join(settings.BASE_DIR, 'templates', 'robots.txt')

        with open(file_path, 'w') as f:
            f.write(robots)

        return json_status.result()


class WebSiteInfoManageView(View):
    def get(self, request):
        import configparser
        import os
        # 初始化
        config = configparser.ConfigParser()
        # 配置文件的绝对路径
        # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        conf_path = os.path.join(settings.BASE_DIR, 'util', 'web_info.ini' )
        # 读取配置文件
        config.read(conf_path, encoding='utf-8')
        # 获取所用的section节点
        # print(config.sections()) # ['webinfo']
        section_node = config.sections()[0]
        # 获取指点section的所用配置信息
        # print(config.items("webinfo")) #[('web_site_name', "''"), ('web_site_domain', "'http://www.qmpython.com:8000'"), ('web_site_title', "''"), ('web_site_keywords', "''"), ('web_site_desc', "''")]

        web_name = config.get(section_node, "WEB_SITE_NAME")
        web_domainname = config.get(section_node, "WEB_SITE_DOMAIN")
        web_title = config.get(section_node, "WEB_SITE_TITLE")
        web_keywords = config.get(section_node, "WEB_SITE_KEYWORDS")
        web_desc = config.get(section_node, "WEB_SITE_DESC")

        context = {
            'web_name': web_name,
            'web_domainname': web_domainname,
            'web_title': web_title,
            'web_keywords': web_keywords,
            'web_desc': web_desc
        }

        return render(request, 'admin/webSite/website_info.html', context=context)


    def post(self, request):
        json_data = request.body
        if not json_data:
            return json_status.params_error(message='参数错误')

        dict_data = json.loads(json_data.decode('utf-8'))

        web_name = dict_data.get('webName', '')
        web_domainname = dict_data.get('webDomainName', '')
        web_title = dict_data.get('indexTitle', '')
        web_keywords = dict_data.get('metaKeywords', '')
        web_desc = dict_data.get('metaDesc', '')

        if not all([web_name, web_domainname, web_title, web_keywords, web_desc]):
            return json_status.params_error(message='数据填写不完整')

        import configparser
        import os
        # 初始化
        config = configparser.ConfigParser()
        # 配置文件的绝对路径
        # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        conf_path = os.path.join(settings.BASE_DIR, 'util', 'web_info.ini' )
        # print(conf_path)
        # 读取配置文件
        config.read(conf_path, encoding='utf-8')
        # 获取所用的section节点
        # print(config.sections()) # ['webinfo']
        section_node = config.sections()[0]

        # # 获取指定section 的options。即将配置文件某个section 内key 读取到列表中：
        # print(config.options("webinfo")) # ['web_site_name', 'web_site_domain', 'web_site_title', 'web_site_keywords', 'web_site_desc']
        # # 获取指点section下指点option的值
        # print(config.get("webinfo", "WEB_SITE_DOMAIN")) # 'http://www.qmpython.com:8000'
        # print(config.get("webinfo", "web_site_desc")) # '描述'
        #
        # # 获取指点section的所用配置信息
        # print(config.items("webinfo")) #[('web_site_name', "''"), ('web_site_domain', "'http://www.qmpython.com:8000'"), ('web_site_title', "''"), ('web_site_keywords', "''"), ('web_site_desc', "''")]

        # 修改某个option的值，如果不存在则会出创建
        config.set(section_node, "WEB_SITE_NAME", web_name)
        config.set(section_node, "WEB_SITE_DOMAIN", web_domainname)
        config.set(section_node, "WEB_SITE_TITLE", web_title)
        config.set(section_node, "WEB_SITE_KEYWORDS", web_keywords)
        config.set(section_node, "WEB_SITE_DESC", web_desc)

        config.write(open(conf_path, "w"))

        data = {
            'web_name': web_name,
            'web_domainname': web_domainname,
            'web_title': web_title,
            'web_keywords': web_keywords,
            'web_desc': web_desc,
        }


        return json_status.result(data=data)


def webuploadImage(request):
    # request.FILES (任何文件都会存在这里面 )
    image_file = request.FILES.get('image_file', '') # xxxx.png
    if not image_file:
        logger.info('从前端获取图片失败')
        return json_status.params_error(message='从前端获取图片失败')

    if image_file.content_type not in ('image/jpeg', 'image/jpg','image/png', 'image/gif', 'image/bmp', 'image/x-icon'):
        return json_status.params_error(message='请上传图片类型文件jpeg,png,jpg,gif,bmp,icon')

    try:
        image_ext_name = image_file.name.split('.')[-1]
    except Exception as e:
        logger.info('图片扩展名异常:{}'.format(e))
        image_ext_name = 'png'

    # 读写文件内容
    import os
    # 获取文件名
    # file_name = image_file.name
    dir_path = os.path.join(settings.BASE_DIR, 'static', 'image')

    upload_type = request.POST.get('image_type', '')
    if upload_type == 'web-logo':
        file_name = 'qmpython_logo.png'

    elif upload_type == 'web-login-register-logo':
        file_name = 'qmpython_login_register_logo.png'

    elif upload_type == 'web-favicon':
        file_name = 'qmpython_favicon.ico'


    file_path = os.path.join(dir_path, file_name)

    # file.chunks() 返回的是一个生成器 能被生成器 不会一次全部使用
    with open(file_path, 'wb') as f:
        for chunk in image_file.chunks():
            f.write(chunk)

    return json_status.result()




#  商城模块
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import renderers
from shop.models import GoodsCategory, GoodsSPU, GoodsSKU
from shop.serializers import GoodsCategorySerializer, GoodsSPUSerializer, GoodsSKUSerializer


class ShoppingCategoriesView(APIView):
    renderer_classes = (renderers.JSONRenderer, renderers.TemplateHTMLRenderer)

    def get(self, request):
        # 获取查询集
        goods_categories = GoodsCategory.objects.only('id')

        goods_serializer = GoodsCategorySerializer(goods_categories, many=True)
        return Response({'goods_categories':goods_categories}, template_name='admin/shop/goods_category_manage.html')

        #return render(request, 'admin/shop/goods_category_manage.html', {'goods_categories': goods_categories})

    def post(self, request):
        # 获取参数
        # 序列化
        serializer_data = GoodsCategorySerializer(data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            return Response(serializer_data.data,status=status.HTTP_201_CREATED)

        return Response(serializer_data.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import mixins
from rest_framework import generics


class ShoppingGoodsSPUsView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):

    queryset = GoodsSPU.objects.all() # 查询结果集
    serializer_class = GoodsSPUSerializer # 序列化类

    def get(self, request, *args, **kwargs):

        #return render(request, 'admin/shop/goods_manage.html')
        return self.list(request,  *args, **kwargs)


    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


from rest_framework import viewsets

class ShoppingGoodsSKUsViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = GoodsSKU.objects.all()
    serializer_class = GoodsSKUSerializer




