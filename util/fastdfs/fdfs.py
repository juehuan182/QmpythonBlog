from fdfs_client.client import Fdfs_client
from django.conf import settings

# 指定fdfs客户端配置文件所在路径
# FDFS_Client = Fdfs_client('/root/src/www/QmpythonBlog/util/fastdfs/client.conf')

FDFS_Client = Fdfs_client(settings.FASTDFS_CLIENT_CONF)


if __name__ == '__main__':
    try:
        ret = FDFS_Client.upload_by_filename('/root/src/www/QmpythonBlog/static/image/qmpython_banner.jpg')
    except Exception as e:
        print("fdfs测试异常：{}".format(e))
    else:
        print(ret)