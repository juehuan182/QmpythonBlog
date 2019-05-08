from django.urls import path
from .views import doc_index, doc_download

from django.views.decorators.cache import cache_page


app_name = 'doc'
urlpatterns = [
    # 资料列表
    path('', doc_index, name='index'),
    # 资料下载
    path('download/<int:doc_id>/', doc_download, name='download'),
 ]

