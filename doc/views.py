import logging
import requests

from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.http import FileResponse, Http404
from django.utils.encoding import escape_uri_path

from .models import Doc
# Create your views here.

logger = logging.getLogger('django')

def doc_index(request):
    docs = Doc.objects.only('id').filter(is_delete=False)

    return render(request, 'doc/docDownload.html', locals())

def doc_download(request, doc_id):
    # 根据id查出文档
    doc = Doc.objects.only('file_url').filter(is_delete=False, id=doc_id).first()
    if doc:
        # http://192.168.31.200:8000/media/avatar.jpeg
        file_url = doc.file_url
        try:
            # requests 返回文件对象
            res = FileResponse(requests.get(file_url, stream=True))
        except Exception as e:
            logger.info('获取文档内容出现异常:\n{}'.format(e))
            raise Http404('文档下载异常')

        # 获取扩展名, 以.分割，获取最后一个
        ex_name = file_url.split('.')[-1]
        if not ex_name:
            raise Http404('文档url异常！')
        else:
            ex_name = ex_name.lower()

        # 设置文件类型，http设置响应头
        if ex_name == "pdf":
            res["Content-type"] = "application/pdf"
        elif ex_name == "zip":
            res["Content-type"] = "application/zip"
        elif ex_name == "doc":
            res["Content-type"] = "application/msword"
        elif ex_name == "xls":
            res["Content-type"] = "application/vnd.ms-excel"
        elif ex_name == "docx":
            res["Content-type"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif ex_name == "ppt":
            res["Content-type"] = "application/vnd.ms-powerpoint"
        elif ex_name == "pptx":
            res["Content-type"] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        else:
            raise Http404("文档格式不正确！")

        doc_filename = escape_uri_path(file_url.split('/')[-1])
        # 设置为inline，会直接打开，attachment为下载文件
        res["Content-Disposition"] = "attachment; filename*=UTF-8''{}".format(doc_filename)
        # 返回一个文件对象 文件响应对象
        return res
    else:
        raise Http404('文档不存在！')
