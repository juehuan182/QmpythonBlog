from django import template
from django.shortcuts import render, get_object_or_404
from django.utils.safestring import mark_safe

from user.models import Account

from datetime import datetime, timedelta

from article.models import Article, Comment

# 将注册类实例化为register对象
register = template.Library()  # 创建一个全局register变量，它是用来注册你自定义标签和过滤器的，只有向系统注册过的tags，系统才认得你。


# register 不能做任何修改，一旦修改，该包就无法引用

# 使用装饰器注册自定义标签
@register.simple_tag
def build_comment_tree(comment_list):
    data = comments(comment_list)
    # 3. 生成html, 注意转换成可以渲染的html
    html = mark_safe(produce_html(data))

    '''
    django从view向template传递HTML字符串的时候，django默认不渲染此HTML，
    原因是为了防止这段字符串里面有恶意攻击的代码。如果需要渲染这段字符串，需要在view里写，则要用到mark_safe    

    '''
    return html


# 筛选出所有的根评论, 整理成列表形式
def comments(comment_list):
    comment_list_dict = {}  # 如果想加快索引(快点找到数据的话)就建一个字典的数据结构,加快索引,节省时间
    for comment in comment_list:  # 循环评论列表，获取列表中的字典
        comment['children'] = []  # 给每个字典添加键值对，给每一条评论加一个{'children':[]}就是让他装对他回复的内容
        comment_list_dict[comment['id']] = comment  # 字典中key为item['id']，value为item存入新的字典
        # 把字典数据结构填上数据,能够加快索引,而且我们数据还是占得原来的内从空间
        # 我们只是引用了数据的内容空间,所以不存在新的数据结构浪费空间一说

    # 若存在父评论将每个评论放进其parent_id对应的children列表中：
    for comment in comment_list_dict:
        # print(comment)  1 2 3 4 5 6 7 ....
        parent_id = comment_list_dict[comment]['parent_id']
        if parent_id:  # 如果parent_id不为空,说明它是子级,要把自己加入对应的父级
            comment_list_dict[parent_id]['children'].append(comment_list_dict[comment])

    # 筛选出所有的根评论, 整理成列表形式
    result = []
    for comment in comment_list_dict:  # 遍历字典得到前面的key
        parent_id = comment_list_dict[comment]['parent_id']
        if not parent_id:  # 如果parent_id为空,说明它是根评论
            result.append(comment_list_dict[comment])

    return result  # 最终只要遍历根节点就可以了。


# 遍历根评论，生成html
def produce_html(comment_dict_list):
    html = ""

    temp = ''' 
                <hr class="m-0">
                <div class="comment-parent flex-left pt-4">
                    <div class="unit-left">
                        <img class="comment-avatar mr-3" src="{0}">
                    </div>
                    <div class="unit-right">
                        <div class="comment-main">
                            <div class="comment-user text-small">
                                <span class="reply_nickname text-muted">{1}</span>
                                <span class="to_nickname text-muted">{2}</span>
                            </div>
                            <div class="comment-body">
                                {3}
                            </div>
                            <div class="comment-footer text-muted">
                                <time class="mr-3" >{4}</time>	
                                <a href="javascript:void(0);" commentId="{5}" id="reply-{5}" class="reply-btn text-muted" onclick="replayComment(this);">回复</a>			
                            </div>
                        </div>	
                    </div>
                </div>

                <div class="comment-children-list mr-4 pt-4">
                    {6}
                </div>
          '''

    for item in comment_dict_list:
        try:
            account = Account.objects.get(pk=item['user_id'])
            nick_name = account.nick_name
            avatar = account.avatar
        except:
            nick_name = 'unknow'

        local_time = item['create_time'] + timedelta(hours=8)
        create_time = datetime.strftime(local_time, "%Y-%m-%d %H:%M:%S")

        if item['parent_id']:  # 如果是子评论，则查询
            # 通过父ip
            account = Account.objects.filter(comment__id=item['parent_id'])
            to_nickname = account[0].nick_name

            if item['children']:  # 如果子评论的子评论
                html += temp.format(avatar, nick_name, '<i class="fa fa-share"></i>' + to_nickname, item['content'].strip(), create_time,
                                    item['id'], '') \
                        + produce_html(item["children"])
            else:  # 如果只是二级评论
                html += temp.format(avatar, nick_name, '<i class="fa fa-share"></i>' + to_nickname, item['content'].strip(), create_time,
                                    item['id'], '')

        else:  # 如果是父评论

            if not item['children']:  # 只有一个父评论
                html += temp.format(avatar, nick_name, '', item['content'].strip(), create_time, item['id'], '')
            else:  # 有子评论的父评论
                html += temp.format(avatar, nick_name, '', item['content'].strip(), create_time, item['id'],
                                    produce_html(item["children"]))

    return html