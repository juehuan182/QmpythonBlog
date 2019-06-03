from article.models import Article, Column, Category
from .serializers import ArticleSerializer, ColumnSerializer, CategorySerializer
from rest_framework.renderers import JSONRenderer
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import generics


def model_to_serializer(request):
    # Model -> Serializer
    serializer = ArticleSerializer(Article.objects.all().first())
    # print(serializer.data) #模型实例转换为python字典数据
    # {'title': '测试2', 'read_num': 80, 'like_num': 0, 'keywords': '测试2', 'description': '这种"互联网软件"采用客户端/服务器模式，建立在分布式体系上，通过互联网通信，具有高延时（high latency）、高并发等特点。\n[TOC]\n理解RESTful架构\n越来越多的人开始意识到，网站即软件，而且是一种新型的软件。\n这种"互联', 'cover_img': 'http://www.qmpython.com:8000/static/image/article/article_cover.jpg'}

    # 除了将模型实例(model	instance)序列化外，我们也能序列化 查询集(querysets)，只需要添加一个序列化参数	many=True
    #serializer = ArticleSerializer(Article.objects.all(), many=True)
    #print(serializer.data)
    '''
        [OrderedDict([('title', '测试2'), ('keywords', '测试2'), ('description',
                                                              '这种"互联网软件"采用客户端/服务器模式，建立在分布式体系上，通过互联网通信，具有高延时（high latency）、高并发等特点。\n[TOC]\n理解RESTful架构\n越来越多的人开始意识到，网站即软件，而且是一种新型的软件。\n这种"互联'),
                      ('cover_img', 'http://www.qmpython.com:8000/static/image/article/article_cover.jpg'),
                      ('read_num', 80), ('like_num', 0)]), OrderedDict([('title', '测试'), ('keywords', '测试关键词'), (
        'description',
        '理解RESTful架构\n越来越多的人开始意识到，网站即软件，而且是一种新型的软件。\n这种"互联网软件"采用客户端/服务器模式，建立在分布式体系上，通过互联网通信，具有高延时（high latency）、高并发等特点。\n网站开发，完全可以采用'),
                                                                        ('cover_img',
                                                                         'http://www.qmpython.com:8000/static/image/article/article_cover.jpg'),
                                                                        ('read_num', 16), ('like_num', 0)]), OrderedDict(
            [('title', 'RESTful架构'), ('keywords', 'RESTful架构,Restful API设计指南'), ('description',
                                                                                 '##理解RESTful架构\n越来越多的人开始意识到，网站即软件，而且是一种新型的软件。\n\n这种"互联网软件"采用客户端/服务器模式，建立在分布式体系上，通过互联网通信，具有高延时（high latency）、高并发等特点。\n\n网站开发，完全'),
             ('cover_img', 'http://www.qmpython.com:8000/static/image/article/article_cover.jpg'), ('read_num', 432),
             ('like_num', 3)]), OrderedDict([('title', '文章标题文章标题'), ('keywords', '文章标题文章标题文章标题文章标题文章标题文章标题文章标题'),
                                             ('description', '文章标题文章标题文章标题文章标题文章标题文章标题fff'),
                                             ('cover_img', 'http://cdn.qmpython.com/qmpython/201903262224/6.jpg'),
                                             ('read_num', 22), ('like_num', 0)])]
    '''

    # python字典转换为json数据
    content = JSONRenderer().render(data=serializer.data)
    # print(content)
    #b'{"title":"\xe6\xb5\x8b\xe8\xaf\x952","keywords":"\xe6\xb5\x8b\xe8\xaf\x952",
    # "description":"\xe8\xbf\x99\xe7\xa7\x8d\\"\xe4\xba\x92\xe8\x81\x94\xe7\xbd\x91\xe8\xbd\xaf\xe4\xbb\xb6\\"\xe9\x87\x87\xe7\x94\xa8\xe5\xae\xa2\xe6\x88\xb7\xe7\xab\xaf/\xe6\x9c\x8d\xe5\x8a\xa1\xe5\x99\xa8\xe6\xa8\xa1\xe5\xbc\x8f\xef\xbc\x8c\xe5\xbb\xba\xe7\xab\x8b\xe5\x9c\xa8\xe5\x88\x86\xe5\xb8\x83\xe5\xbc\x8f\xe4\xbd\x93\xe7\xb3\xbb\xe4\xb8\x8a\xef\xbc\x8c\xe9\x80\x9a\xe8\xbf\x87\xe4\xba\x92\xe8\x81\x94\xe7\xbd\x91\xe9\x80\x9a\xe4\xbf\xa1\xef\xbc\x8c\xe5\x85\xb7\xe6\x9c\x89\xe9\xab\x98\xe5\xbb\xb6\xe6\x97\xb6\xef\xbc\x88high latency\xef\xbc\x89\xe3\x80\x81\xe9\xab\x98\xe5\xb9\xb6\xe5\x8f\x91\xe7\xad\x89\xe7\x89\xb9\xe7\x82\xb9\xe3\x80\x82\\n[TOC]\\n\xe7\x90\x86\xe8\xa7\xa3RESTful\xe6\x9e\xb6\xe6\x9e\x84\\n\xe8\xb6\x8a\xe6\x9d\xa5\xe8\xb6\x8a\xe5\xa4\x9a\xe7\x9a\x84\xe4\xba\xba\xe5\xbc\x80\xe5\xa7\x8b\xe6\x84\x8f\xe8\xaf\x86\xe5\x88\xb0\xef\xbc\x8c\xe7\xbd\x91\xe7\xab\x99\xe5\x8d\xb3\xe8\xbd\xaf\xe4\xbb\xb6\xef\xbc\x8c\xe8\x80\x8c\xe4\xb8\x94\xe6\x98\xaf\xe4\xb8\x80\xe7\xa7\x8d\xe6\x96\xb0\xe5\x9e\x8b\xe7\x9a\x84\xe8\xbd\xaf\xe4\xbb\xb6\xe3\x80\x82\\n\xe8\xbf\x99\xe7\xa7\x8d\\"\xe4\xba\x92\xe8\x81\x94","cover_img":"http://www.qmpython.com:8000/static/image/article/article_cover.jpg","read_num":80,"like_num":0}'

    # 反序列化类似，将流(stream)解析成原生数据类型字典...stream->json

    stream = BytesIO(content)  # <_io.BytesIO object at 0x7f957d6a8f10>
    data = JSONParser().parse(stream)
    # print(data) #{'like_num': 0, 'description': '这种"互联网软件"采用客户端/服务器模式，建立在分布式体系上，通过互联网通信，具有高延时（high latency）、高并发等特点。\n[TOC]\n理解RESTful架构\n越来越多的人开始意识到，网站即软件，而且是一种新型的软件。\n这种"互联', 'read_num': 80, 'title': '测试2', 'cover_img': 'http://www.qmpython.com:8000/static/image/article/article_cover.jpg', 'keywords': '测试2'}

    # 将python字典数据恢复成正常的对象实例...
    serializer = ArticleSerializer(data=data)
    # print(serializer.is_valid()) # True
    # print(serializer.data)
    # {'title': '测试2', 'like_num': 0, 'description': '这种"互联网软件"采用客户端/服务器模式，建立在分布式体系上，通过互联网通信，具有高延时（high latency）、高并发等特点。\n[TOC]\n理解RESTful架构\n越来越多的人开始意识到，网站即软件，而且是一种新型的软件。\n这种"互联', 'keywords': '测试2', 'cover_img': 'http://www.qmpython.com:8000/static/image/article/article_cover.jpg', 'read_num': 80}
    # print(serializer.validated_data )
    # OrderedDict([('title', '测试2'), ('keywords', '测试2'), ('description', '这种"互联网软件"采用客户端/服务器模式，建立在分布式体系上，通过互联网通信，具有高延时（high latency）、高并发等特点。\n[TOC]\n理解RESTful架构\n越来越多的人开始意识到，网站即软件，而且是一种新型的软件。\n这种"互联'), ('cover_img', 'http://www.qmpython.com:8000/static/image/article/article_cover.jpg'), ('read_num', 80), ('like_num', 0)])


from django.http import HttpResponse

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)



class ColumnView(generics.ListCreateAPIView):

    queryset = Column.objects.all()  # 查询结果集
    serializer_class = ColumnSerializer # 序列化类


class ColumnFilterView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Column.objects.all()
    serializer_class = ColumnSerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()  # 查询结果集
    serializer_class = CategorySerializer  # 序列化类




# 分页自定义
from rest_framework.pagination import PageNumberPagination
class ArticlePagination(PageNumberPagination):
    page_size = 4 # 表示每页的默认显示数量
    page_size_query_param = 'page_size' # 表示url中每页数量参数
    page_query_param = 'p' # 表示url中的页码参数
    max_page_size = 100  # 表示每页最大显示数量，做限制使用，避免突然大量的查询数据，数据库崩溃


class ArticleListleView(generics.ListCreateAPIView):

    queryset = Article.objects.all()  # 查询结果集
    serializer_class = ArticleSerializer # 序列化类
    pagination_class = ArticlePagination   # 自定义分页会覆盖settings全局配置的


class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()  # 查询结果集
    serializer_class = ArticleSerializer  # 序列化类

from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .filters import AriticleFilter

class ArticleViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Article.objects.all()  # 查询结果集
    serializer_class = ArticleSerializer # 序列化类
    pagination_class = ArticlePagination   # 自定义分页会覆盖settings全局配置的
    # 过滤器 过滤，搜索，排序
    filter_backends = (DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter)
    # 如果要允许对某些字段进行过滤，可以使用filter_fields属性。
    #filter_fields = ('title', 'category')
    # 使用自定义过滤器
    filter_class = AriticleFilter
    # 搜索
    search_fields = ('title', 'description', 'content')
    # 排序
    ordering_fields = ('id', 'read_num')

    # Token认证
    from rest_framework.permissions import IsAuthenticated
    permission_classes = (IsAuthenticated,)

    # def get_queryset(self):
    #     queryset = Article.objects.all()
    #     read_num = self.request.query_params.get('read_num', 0)
    #
    #     if read_num:
    #         queryset = queryset.filter(read_num__gt=int(read_num))
    #
    #     return queryset


# def article_detail(request, article_id):
#     try:
#         article = Article.objects.get(pk=article_id)
#     except Article.DoesNotExist:
#         return HttpResponse(status=404)
#
#     if request.method == 'GET':
#         serializer = ArticleSerializer(article)
#         return JSONResponse(serializer.data)
#     elif request.method == 'PUT':
#         data = JSONParser().parse(request)
#         serializer = ArticleSerializer(article, data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return JSONResponse(serializer.data)
#         return JSONResponse(serializer.errors, status=400)
#
#     elif request.method == 'DELETE':
#         article.delete()
#         return HttpResponse(status=204)



from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

# @api_view(['GET', 'POST'])
# def article_list(request, format=None):
#     if request.method == 'GET':
#         articles = Article.objects.all()
#         serializer = ArticleSerializer(articles, many=True)
#         return Response(serializer.data) #	根据客户端的请求来渲染成指定的内容类型。
#
#     elif request.method == 'POST':
#         serializer = ArticleSerializer(data=request.data)   #request.data  # 处理任意数据， 可供 'POST', 'PUT' and 'PATCH' 请求使用
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# request.data  # 处理任意数据， 可供 'POST', 'PUT' and 'PATCH' 请求使用
# 	request.data	能够处 理	json	请求，但是它也能处理其他格式。
# 	相似地，虽然我们可以在响应对象中带 数据，但允许REST框架渲染响应成正确的内容类型。

# 基于类视图实现
from rest_framework.views import APIView
# class articleDetailView(APIView):
#     def get(self, request, article_id, format=None):
#         try:
#             article = Article.objects.get(pk=article_id)
#         except Article.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#
#         serializer = ArticleSerializer(article)
#         return Response(serializer.data)
#
#     def put(self, request, article_id, format=None):
#         try:
#             article = Article.objects.get(pk=article_id)
#         except Article.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#
#         #data = JSONParser().parse(request)
#         serializer = ArticleSerializer(article, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, article_id, format=None):
#         try:
#             article = Article.objects.get(pk=article_id)
#         except Article.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#
#         article.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)



# 使用混合类
from rest_framework import mixins
from rest_framework import generics
#
# class articleListView(mixins.ListModelMixin,
#                       mixins.CreateModelMixin, # 混合类mixins提供.list和.create方法
#                       generics.GenericAPIView):  # 基类提供核心功能
#
#     queryset = Article.objects.all()
#     serializer_class = ArticleSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)
#
#
# class articleDetailView(mixins.RetrieveModelMixin,
#                         mixins.UpdateModelMixin,
#                         mixins.DestroyModelMixin,
#                         generics.GenericAPIView):
#
#     queryset = Article.objects.all()
#     serializer_class = ArticleSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)
#
#
#     def put(self, request, *args, **kwargs):
#         return self.update(request, *args, **kwargs)
#
#     def delete(self, request, *args, **kwargs):
#         return self.destroy(request, *args, **kwargs)
#


# 基于视图一般类generic class
from rest_framework import permissions
from .permissions import IsOwnerOrReadOnly
#
# class ArticleListView(generics.ListCreateAPIView):
#     permission_classes = (permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly) # IsAuthenticatedOrReadOnly类，确保授权请求有读写权限，而没有授权用户只有读权限。
#
#     queryset = Article.objects.all()
#     serializer_class = ArticleSerializer
#
#     def perform_create(self, serializer):
#         serializer.save(author=self.request.user) # 当我们的serializer里create()方法被调用时，将自动添加'owner'字段和验证合法的请求数据。


class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly)

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


from user.models import Account
from .serializers import AccountSerializer

class AccountList(generics.ListAPIView):

    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class AccountDetail(generics.RetrieveAPIView):

    queryset = Account.objects.all()
    serializer_class = AccountSerializer


from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'articles': reverse('article-list', request=request, format=format)
    })