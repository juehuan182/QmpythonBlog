from django.urls import path
from django.conf.urls import include

from rest_framework.routers import DefaultRouter


from .views import index, ColumnManageView, ColumnEditView, getColumnList, CategoryManageView, CategoryEditView, TagManageView, \
    AdvertisingManageView, AdvertisingEditView, FriendlinkManageView, FriendlinkEditView, AdvertisingAddView, TagEditView, ArticleManageView, ArticleEditView,\
    RecommendArticleManageView, RecommendArticleAddView, ShoppingGoodsSKUsViewset, WebSiteUrlsView, \
    RecommendArticleEditView, ArticlesByCategoryIdView, DocsManageView, DocsEditView, DocsPubView, DbBackupView, \
    CommentsManageView, CommentsEditView, GroupManagerView, UserGroupManageView, ArticleAddView, markDownUploadImage, upload_to_qiniu, uploadFileToServer,\
    GroupAddView, GroupEditView, viewGroup, UserGroupEditView, UserGroupAddView, getGroupUser, UserInfoView, UserInfoEditView,\
    ProhibitedWordsManageView, RobotsManageView, WebSiteInfoManageView, webuploadImage, ShoppingCategoriesView, ShoppingGoodsSPUsView



app_name = 'admin'

router = DefaultRouter()
router.register('shop/goodsSKUs', ShoppingGoodsSKUsViewset)


urlpatterns = [
    path('index/', index, name='index'),

    #  文章栏目
    path('column/',ColumnManageView.as_view(), name='column_manage'),
    path('column/<int:column_id>/', ColumnEditView.as_view(), name='column_edit'),
    # 获取栏目列表
    path('column/list/', getColumnList, name='column_list'),

    #   文章分类
    path('category/', CategoryManageView.as_view(), name='category_manage'),
    path('category/<int:category_id>/', CategoryEditView.as_view(), name='category_edit'),


    #   文章标签
    path('tag/', TagManageView.as_view(), name='tag_manage'),
    path('tag/<int:tag_id>/', TagEditView.as_view(), name='tag_edit'),

    #   文章
    path('article/', ArticleManageView.as_view(), name='article_manage'),
    path('article/<int:article_id>/', ArticleEditView.as_view(), name='article_edit'),
    path('article/add/', ArticleAddView.as_view(), name='article_add'),

    # 推荐文章
    path('recommendarticle/', RecommendArticleManageView.as_view(), name='recommend_article_manage'),
    path('recommendarticle/add/', RecommendArticleAddView.as_view(), name='recommend_article_add'),
    path('recommendarticle/<int:recommendarticle_id>/', RecommendArticleEditView.as_view(), name='recommend_article_edit'),
    path('articlesByCategoryId/', ArticlesByCategoryIdView.as_view(), name='articles_by_categoryid'),

    # markdown上传图片
    path('markdown/image/', markDownUploadImage, name='markdown_image_upload'),

    # 上传图片至服务器
    # path('uploadImageToServer/', uploadImageToServer, name='uploadImage'),
    # 上传至七牛云
    # path('uploadToken/', upload_to_qiniu, name='up_token'),
    path('uploadQiniu/', upload_to_qiniu, name='upload_qi_niu'),

    # 上传文件
    path('uploadFileToServer/', uploadFileToServer, name='uploadFile'),

    # 广告
    path('advertising/', AdvertisingManageView.as_view(), name='advertising_manage'),
    path('advertising/<int:advertising_id>/', AdvertisingEditView.as_view(), name='advertising_edit'),
    path('advertising/add/', AdvertisingAddView.as_view(), name='advertising_add'),

    # 友情链接
    path('friendlinks/', FriendlinkManageView.as_view(), name='friendlink_manage'),
    path('friendlinks/<int:friendlink_id>/', FriendlinkEditView.as_view(), name='friendlink_edit'),

    # 文档
    path('docs/', DocsManageView.as_view(), name='docs_manage'),
    path('docs/<int:doc_id>/', DocsEditView.as_view(), name='docs_edit'),
    path('docs/pub/', DocsPubView.as_view(), name='docs_pub'),

    # 评论信息
    path('comments/', CommentsManageView.as_view(), name='comments_manage'),
    path('comments/<int:comment_id>/', CommentsEditView.as_view(), name='comments_edit'),


    # 权限相关
    path('group/', GroupManagerView.as_view(), name='group_manage'),
    path('group/add/', GroupAddView.as_view(), name='group_add'),
    path('group/<int:group_id>/', GroupEditView.as_view(), name='group_edit'),
    path('group/view/<int:group_id>/', viewGroup, name='group_view'),

    #  用户管理
    path('user_group/', UserGroupManageView.as_view(), name='user_group_manage'),
    path('user_group/edit/<int:user_id>/', UserGroupEditView.as_view(), name='user_group_edit'),
    path('user_group/add/', UserGroupAddView.as_view(), name='user_group_add'),

    path('group/user/', getGroupUser,name='get_group_user'),

    # 用户信息
    path('user_info/', UserInfoView.as_view(),name='user_info_manage'),
    path('user_info/edit/<int:user_id>/', UserInfoEditView.as_view(), name='user_info_edit'),

    # 违禁词
    path('prohibited_words/', ProhibitedWordsManageView.as_view(), name='prohibitedWords_manage'),

    # Robots设置
    path('robots/', RobotsManageView.as_view(), name='robots'),

    # 数据库备份
    path('dbbackup/', DbBackupView.as_view(), name='dbbackup'),

    # web网站信息
    path('website_info/', WebSiteInfoManageView.as_view(), name='website_info'),
    path('website_info/upload_image/', webuploadImage, name='web_uploadImage'),

    # 百度链接提交
    path('website_urls/', WebSiteUrlsView.as_view(), name='website_urls'),

    # 商城模块
    # 商品分类
    path('shop/categories/', ShoppingCategoriesView.as_view(), name='shop_categories'),

    # 商品信息
    path('shop/goodsSPUs/', ShoppingGoodsSPUsView.as_view(), name='shop_goodsSPUs'),


    path('', include(router.urls)),

]
