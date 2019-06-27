from django.urls import path
from django.conf.urls import include, re_path
from .views import ArticleListleView,ArticleDetailView, AccountList, AccountDetail, api_root, ColumnView, ColumnFilterView,\
                    CategoryDetailView, ArticleViewSet
from rest_framework.urlpatterns import format_suffix_patterns

from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

app_name = 'api'


# article_list = ArticleViewSet.as_view({
#     'get': 'list',
#     'post': 'create'
# })


router = DefaultRouter()
router.register('articles', ArticleViewSet)


urlpatterns = [
    path('columns/', ColumnView.as_view(), name='columns'),
    path('columns/<int:pk>/', ColumnFilterView.as_view(), name='columns_filter'),


    # path('articles/', ArticleListleView.as_view(), name='article_list' ),
    #path('articles/', article_list, name='article_list'),
    path('', include(router.urls)),
    #re_path(r'^', include(router.urls)),
    #path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),



    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),

    path('account_list/', AccountList.as_view(), name='account_list'),
    path('account_detail/<int:article_id>/', AccountDetail.as_view(), name='account_detail'),

    #path('', api_root, name='api_root'),
    re_path(r'^api-token-auth/', obtain_jwt_token),

]

#urlpatterns	= format_suffix_patterns(urlpatterns)
