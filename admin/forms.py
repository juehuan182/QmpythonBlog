from django import forms

from article.models import Article, Category, Advertising
from doc.models import Doc
from course.models import Course


from util.forms import FormMixin


# 使用forms.ModelForm
# 除了利用表单类forms.Form，还有更进一步的方法，那就是整合model模型和forms表单，
# 连表单类都不用写，直接使用数据模型forms.ModelForm生成表单类,注意前端表单与model字段名称也一样对应；

class ArticleAddForm(forms.ModelForm, FormMixin):
    """
      1.补充 Model 没有的 Field 到表单
      2.覆盖 Model 中的 Field 定义
    """
    category = forms.ModelChoiceField(queryset=Category.objects.only('id'), error_messages={"required": "文章分类id不能为空",
                                                                                            "invalid_choice": "文章分类id不存在"})
    class Meta:
        model = Article   #  说明要引用的models类
        fields = ['title', 'keywords', 'description', 'category', 'content', 'cover_img', 'tag']  # 说明要关联类中的哪些字段,# exclude 排除
        error_messages = {
            'title': {
                'max_length': "文章标题长度不能超过35",
                'min_length': "文章标题长度不能少于1",
                'required': "文章标题不能为空",
            },
            'keywords': {
                'max_length': "文章关键词长度不能超过60",
                'min_length': "文章关键词长度不能少于1",
                'required': "文章关键词不能为空",
            },
            'description': {
                'max_length': "文章描述长度不能超过120",
                'min_length': "文章描述长度不少于1",
            },
            'content': {
                'required': "文章内容不能为空",
            }

        }


class AdvertisingAddForm(forms.ModelForm, FormMixin):

    class Meta:
        model = Advertising
        exclude = ['create_time', 'update_time', 'is_delete', 'click_num']
        error_messages = {
            'name': {
                'max_length': '广告名称不能超过50位',
                'min_length': '广告名称不能少于1位',
                'required': '广告名称不能为空'
            },
            'image_url': {
                'required': '广告图片不能没有'
            },
            'link_to': {
                'required': '链接地址不能为空'
            },
            'position':{
                'required': '选择投放位置'
            },
            'sort': {
                'required': '优先级不能为空'
            },
            'end_time': {
                'required': '结束日期不能为空'
            }
        }




class DocPubForm(forms.ModelForm, FormMixin):

    class Meta:
        model = Doc
        fields = ['title', 'desc', 'image_url', 'file_url']
        error_messages = {
            'title': {
                'max_length': "文档标题长度不能超过30",
                'min_length': "文档标题长度不能少于1",
                'required': "文档标题不能为空",
            },
            'desc': {
                'max_length': "文档描述长度不能超过200",
                'min_length': "文档描述长度不能少于1",
                'required': "文档描述不能为空",
            },
            'image_url': {
                'required': '文档缩略图url不能为空'
            },
            'file_url': {
                'required': '文档url不能为空'
            }
        }


class CoursePubForm(forms.ModelForm, FormMixin):
    class Meta:
        model = Course
        exclude = ['create_time', 'update_time', 'is_delete']
        error_messages = {
            'title': {
                'max_length': "课程标题长度不能超过50",
                'min_length': "课程标题长度不能少于1",
                'required': "课程标题不能为空",
            },
            'cover_url': {
                'required': "课程封面图URL不能为空",
            },
            'video_url': {
                'required': "课程视频URL不能为空",
            },
            'duration': {
                'required': "课程时长不能为空",
            },
            'desc': {
                'required': "课程简介不能为空",
            },
            'outline': {
                'required': "课程大纲不能为空",
            },
            'lectuer': {
                'required': "课程讲师不能为空",
            },
            'course_category': {
                'required': "课程分类不能为空",
            }
        }

