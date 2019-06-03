from rest_framework import serializers
from article.models import Article, Category, Tag, Column
from user.models import Account

class ColumnSerializer(serializers.ModelSerializer):
    categories = serializers.StringRelatedField(many=True)  # 字段名必须设置related_name 或者使用表名_set 就行了

    class Meta:
        model = Column
        fields = ['id','name', 'link_url', 'index','categories']


class CategorySerializer(serializers.ModelSerializer):
    column = ColumnSerializer()
    class Meta:
        model = Category
        fields = ['id','name', 'column']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


# class ArticleSerializer(serializers.ModelSerializer):
#         # view_name表示路由的别名,注意如果不是根目录下，则需要使用命名空间来：，
#         # lookup_field:根据表指定字段，来拼路径，生成链接
#         # lookup_url_kwarg：默认是pk，（urls.py中的指定的pk）可以不写，反向解析有名分组的名字。
#         #category = serializers.HyperlinkedIdentityField(view_name='api:category_detail', lookup_field='category_id', lookup_url_kwarg='pkx')
#         class Meta:
#             model = Article
#             fields = ['id', 'title', 'keywords', 'description', 'cover_img', 'read_num', 'like_num', 'category', 'tag', 'author']
#


class ArticleSerializer(serializers.Serializer):  # 与django的表单类相似
    id = serializers.IntegerField()
    title = serializers.CharField(label='标题', min_length=1, max_length=35, required=True,
                                  error_messages={'required': '标题不能为空',
                                                  'max_length': '标题不能超过35个字符',
                                                  'min_length': '标题不能小于1个字符'
                                                  })
    keywords = serializers.CharField(label='关键字', max_length=50, required=False)
    description = serializers.CharField(label='描述', max_length=120, allow_blank=True, required=False)
    # content = serializers.CharField()
    cover_img = serializers.URLField(label='封面图', allow_blank=True)
    read_num = serializers.IntegerField(label='浏览量', default=0)
    like_num = serializers.IntegerField(label='点赞数', default=0)
    # 分类名称
    #category = serializers.CharField(source='category.name', label='所属类别')  #多对一关系
    #author = serializers.CharField(source='author.nick_name', label='作者')

    # SerializerMethodField(),表示自定义显示 然后写一个自定义的方法get_字段名
    #tag = serializers.SerializerMethodField() #多对多关系

    category = serializers.StringRelatedField(many=False)

    author = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())  # 一方不需要用many
    # 不过这样只是用户获得的只是一个外键类别的id，并不能获取到详细的信息，如果想要获取到具体信息，那需要嵌套serializer
    #author = AccountSerializer()   # author一定要是article model中存在的字段
    tag = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())  # 多对多用many=True



    def get_tag(self, obj):
        tags = obj.tag.all()
        tag_list = []
        for tag in tags:
            tag_list.append({'pk':tag.pk, 'name': tag.name})  # 列表里面需要序列化形式

        return tag_list


    def validate_title(self, title):  # 注意函数名写法，validate_ + 字段名字 ，类似form表单类自定义
        if title.strip():  # 注意参数，self以及字段名
            raise serializers.ValidationError('用户已经存在')

    #上面验证方式，只能验证一个字段，如果要自定义多个，则需要写对应个数方法验证，
    # 如果是两个字段联合在一起进行验证，那么我们就可以重载validate()方法。
    def validate(self, attrs):
        # 传进来什么参数，就返回什么参数，一般情况下用attrs
        if attrs['read_num'] < attrs['like_num']:
            raise serializers.ValidationError("不正常，数据问题")
        return attrs



    def create(self, validated_data): # create()和update()方法定义了在调用serializer.save()时成熟的实例是如何被创建和修改的。
        return Article.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.keywords = validated_data.get('keywords', instance.keywords)
        instance.description = validated_data.get('description', instance.description)
        instance.content = validated_data.get('content', instance.content)
        instance.cover_img = validated_data.get('cover_img', instance.cover_img)
        instance.read_num = validated_data.get('read_num', instance.read_num)
        instance.like_num = validated_data.get('like_num', instance.like_num)

        instance.save()
        return instance
#
    #
    # '''
    # label表示标签,是在HTML页面显示api时,显示的字段名称.
    # read_only表示该字段只用于序列化输出.也就是只可以读他,在返回的时候可以返回他,接收的时候不需要接收他,因为是自增的.
    # required 表示是否是必填项,false表示是非必须.
    # 参数名称 说明
    # read_only 表明该字段仅用于序列化输出，默认False
    # write_only 表明该字段仅用于反序列化输入，默认False
    # required 表明该字段在反序列化时必须输入，默认True
    # default 反序列化时使用的默认值
    # allow_null 表明该字段是否允许传入None，默认False
    # validators 该字段使用的验证器
    # error_messages 包含错误编号与错误信息的字典
    # label 用于HTML展示API页面时，显示的字段名称
    # help_text 用于HTML展示API页面时，显示的字段帮助提示信息
    # '''


# class ArticleSerializer(serializers.ModelSerializer):
#     # author = serializers.ReadOnlyField(source='author.username')
#     # 外键的field也比较简单，如果我们直接使用serializers.Serializer，那么直接用PrimaryKeyRelatedField就解决了。
#     # author = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
#     # 不过这样只是用户获得的只是一个外键类别的id，并不能获取到详细的信息，如果想要获取到具体信息，那需要嵌套serializer
#     #author = AccountSerializer()   # author一定要是article model中存在的字段
#     #category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # 一方不需要用many
#     #tag = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())  # 多对多用many=True
#
#     category = serializers.CharField(source='category.name', label='所属类别')  #多对一关系
#     author = serializers.CharField(source='author.nick_name', label='作者')
#
#     # SerializerMethodField(),表示自定义显示 然后写一个自定义的方法get_字段名
#     tag = serializers.SerializerMethodField() #多对多关系
#
#     def get_tag(self, obj):
#         tags = obj.tag.all()
#         tag_list = []
#         for tag in tags:
#             tag_list.append({'pk': tag.pk, 'name': tag.name})  # 列表里面需要序列化形式
#
#         return tag_list
#
#     class Meta:
#         model = Article
#         fields = ['id', 'title', 'keywords', 'description', 'cover_img', 'read_num', 'like_num', 'category', 'tag', 'author']


from user.models import Account

class AccountSerializer(serializers.ModelSerializer):
    # 注意：ArticleSerializer中几种方式，外键都是正向取得，下面介绍怎么反向去取，如，我们需要获取用户下，发表多少篇文章。
    # 首先，在课程文章的model中，需要在外键中设置related_name
    # 反向取文章，通过related name
    # 一对多，一个用户发表多篇文章，一定要设定many=tre
    #articles = ArticleSerializer(many=True)  # articles 是设置related_name的名称

    class Meta:
        model = Account
        fields = ['id', 'username', 'email', 'articles']



# 之前我们的 api 都是用外键关联，然而实际上用超链接的方式更符合 RESTful 的思想。
# 使用超链接 HyperlinkedModelSerializer 替代 ModelSerializer
# 现在我们在实例之间用超链接形式，我们需要修改我们的serializers，用HyperlinkedModelSerializer代替ModelSerializer,
# 修改后将有如下不同：
# 1.HyperlinkedModelSerializer默认不包含pk field
# 2.HyperlinkedModelSerializer会自动包括url field
# 3.关系使用的是HyperlinkedRelatedField而不是PrimaryKeyRelatedField
#
# class ArticleSerializer(serializers.HyperlinkedModelSerializer):
#     # author = serializers.ReadOnlyField(source='author.username')
#     # 外键的field也比较简单，如果我们直接使用serializers.Serializer，那么直接用PrimaryKeyRelatedField就解决了。
#     # author = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
#     # 不过这样只是用户获得的只是一个外键类别的id，并不能获取到详细的信息，如果想要获取到具体信息，那需要嵌套serializer
#     #author = AccountSerializer()   # author一定要是article model中存在的字段
#     # category = serializers.HyperlinkedRelatedField(read_only=True, view_name='categories')  # 一方不需要用many
#     # tag = serializers.HyperlinkedRelatedField(many=True, queryset=Tag.objects.all(), view_name='tags')  # 多对多用many=True
#
#     class Meta:
#         model = Article
#         fields = ['title', 'keywords', 'description', 'cover_img', 'read_num', 'like_num']