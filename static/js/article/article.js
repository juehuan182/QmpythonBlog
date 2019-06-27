
/*点赞*/
function likeArticle(article_id) {
    //限制一个ip只能点赞一次，否则弹框提示已提交不能再提交，后面的不能执行。

    //创建异步对象
    let xhr = new XMLHttpRequest();

    //请求行
    let url = "/articles/" + article_id + "/likes/";
    xhr.open('POST', url);
    //请求头
    //post方式，使用post提交的时候需要设置content-type为"application/x-www-form-urlencoded"
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded; charset=utf-8");
    var csrftoken = Cookies.get('csrftoken');
    xhr.setRequestHeader("X-CSRFToken", csrftoken);

    //post请求发送数据写在send中，key=value&key2=value2
    xhr.send();

    //注册回调函数
    //请求响应回来之后触发
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            //获取返回的数据
            var data = JSON.parse(xhr.responseText); //将后端传过来的json数据解析为对象
            // console.log(data.like_nums);
            if (data.add_flag) {
                var thumbsSpan = document.querySelector(".thumbs-up>span");
                var metaSpan = document.querySelector(".article-meta>span.like>span");
                thumbsSpan.innerHTML = data.likes_nums;
                metaSpan.innerText = data.likes_nums;
                message.showSuccess("谢谢老铁的赞~~");
            } else {
                message.showInfo("兄die，您已赞过，谢谢~~");
            }
        }
    };

}

//打赏
function payToggle() {
    var rewardBox = document.getElementsByClassName("reward-box");
    var hideBox = document.getElementsByClassName("hide-box");

    rewardBox[0].style.display = "block";
    hideBox[0].style.display = "block";
}

//弹出框关闭
function closeDig() {
    var rewardBox = document.getElementsByClassName("reward-box");
    var hideBox = document.getElementsByClassName("hide-box");

    rewardBox[0].style.display = "none";
    hideBox[0].style.display = "none";

}

//微信，支付宝二维码切换
var payType = document.querySelectorAll(".payment-method .pay-type");
var index = 0;

for (var i = 0; i < payType.length; i++) {

    payType[i].setAttribute("aa", i);

    payType[i].onclick = function () {
        /*清除上一个*/
        payType[index].style.cssText = "border-color: #909090;color: #909090;";
        /*移除类名*/
        index = this.getAttribute("aa");

        /*变成对应二维码*/
        var payCodeImg = document.querySelector(".pay-code img");

        if (index == 0) {
            this.style.cssText = "border-color: #55acee;color: #55acee;";
            payCodeImg.src = "/static/image/payment/alipay.png";
        } else {
            this.style.cssText = "border-color: #00bb29;color: #00bb29;";
            payCodeImg.src = "/static/image/payment/wxpay.png";
        }
    };
}


// /*文章分享*/
function shareAction(type, title, summary, image) {
    console.log(image);
    var url = window.location.href;  //获取页面完整地址
    //获取域名
    var host = "http://" + window.location.host;

    if (type === "weixin") {

        var shareWechat = document.querySelector(".share-wechat");
        var shareCode = document.querySelector(".share-code");
        shareWechat.style.display = "block";

        // 设置参数方式
        var qrcode = new QRCode(shareCode, {   //显示二维码的元素或该元素的ID
            text: url,  //需要加上http://开头
            width: 120,
            height: 120,
            colorDark: '#000000',
            colorLight: '#ffffff',
            correctLevel: QRCode.CorrectLevel.H
        });

    } else {

        if (type === "sina") {
            url = "http://v.t.sina.com.cn/share/share.php?&url=" + url + "&title=全民学python-" + title + "&pic=" + host + image + "&appkey=1100417222";
        } else if (type === "qzone") {
            url = "http://sns.qzone.qq.com/cgi-bin/qzshare/cgi_qzshare_onekey?url=" + url + "&title= 全民学python-" + title + "&summary=我在全民学python学习“" + summary + "”&pics=" + host + image;
        } else if (type === "qq") {
            url = "http://connect.qq.com/widget/shareqq/index.html?url=" + url + "&title=全民学python-" + title + "&summary=我在全民学python学习“" + summary + "&desc=我在全民学python学习“Python技术分享”哟，干货十足，收获满满，你也来看看吧~。每天学一点，进步一点点工作生活更美好~&pics=" + host + image;

        }
        //window.open(URL,name,features,replace) 方法用于打开一个新的浏览器窗口或查找一个已命名的窗口
        window.open(url, 'height=100,width=100,top=100,left=100');
    }
}


function closeShare() {
    var shareWechat = document.querySelector(".share-wechat");
    shareWechat.style.display = "none";
}


/*评论功能*/
var parent_comment_id = "";  // 设置全局变量,当点击回复按钮则赋值为点击的评论的id;
var parent_comment_usename = ""; //父级usename

//获取文本框对象
var contentArea = document.querySelector("div.edit-comments>textarea");

//获取评论按钮对象
var commentBtn = document.querySelector("button.comment-btn");

var replyDiv = "";

//回复评论事件
function replayComment(_this) {

    //检查是否登录
    var comments = document.querySelector(".article-comments");
    var flag = parseInt(comments.getAttribute("is_login"));
    if (flag != 1) {
        //window.location.href = "/account/login/";
        message.showInfo("您尚未登录，请 登录 或 注册 后评论");
        return;

    }

    //获取针对哪个评论回复的id,传给后端
    parent_comment_id = _this.getAttribute("commentId");
    //获取父级评论usename
    parent_comment_usename = _this.parentNode.parentNode.firstElementChild.firstElementChild.innerText;
    //给文本框添加回复的用户名内容, 仅用于在前端显示,
    contentArea.value = "@" + parent_comment_usename + ":\n";

    //2、获取子评论最外层区域
    //获取当前点击的父元素
    replyDiv = _this.parentNode.parentNode.parentNode.parentNode.parentNode;
    if (replyDiv.className == "comments-list") {  //如果是根评论的回复
        replyDiv = _this.parentNode.parentNode.parentNode.parentNode.nextElementSibling; //nextElementSibling获取下个兄弟节点

    }

    // 3、聚焦到评论框
    contentArea.focus();
}


//动态增加文章评论
if (commentBtn){
    commentBtn.onclick = function () {
    //取出输入的评论内容
    // 1. 取出换行符 \n 的索引位置
    var index = contentArea.value.indexOf("\n");  //indexOf() 方法可返回某个指定的字符串值在字符串中首次出现的位置。如果要检索的字符串值没有出现，则该方法返回 -1。
    // 2. 取出真正的文本内容,字符串切片,js语法,从第二行开始,切片所有的内容
    var new_content = contentArea.value.substr(index + 1);  //substr() 方法可在字符串中抽取从 start 下标开始的指定数目的字符。
    if (new_content.length == 0) {
        message.showError("评论内容不能为空！");
        return;
    }

    // console.log(new_content);
    new_content = safeStr(new_content);
    // console.log(typeof (new_content));


    //获取当前文章id
    var article_id = this.getAttribute('data-article-id');  //获取标签中data-* 属性
    //获取需要请求的url
    var URL = "/articles/" + article_id + "/comments/";
    //创建对象 异步对象
    var xhr = new XMLHttpRequest();

    //请求行
    xhr.open('post', URL);

    //请求头setRequestHeader
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded; charset=utf-8");
    var csrftoken = Cookies.get('csrftoken');
    xhr.setRequestHeader("X-CSRFToken", csrftoken);

    //注册回调函数
    xhr.onreadystatechange = function (ev) {

        if (xhr.readyState == 4 && xhr.status == 200) {
            var data = JSON.parse(xhr.responseText); //由JSON字符串转换为JSON对象
            // console.log(data);
            // console.log(data['created_time']);
            //如果是根评论，则在根区域拼接
            //获取根区域
            var divComments = document.querySelector("div.comments-list");

            var commentsHtml = divComments.innerHTML;
            // console.log('pared='+parent_comment_id);
            var replyHtml = replyDiv.innerHTML;

            //评论内容模板
            temp = '<hr class="m-0">\n' +
                '                <div class="comment-parent flex-left pt-4">\n' +
                '                    <div class="unit-left">\n' +
                '                        <img class="comment-avatar mr-3" src="{0}">\n' +
                '                    </div>\n' +
                '                    <div class="unit-right">\n' +
                '                        <div class="comment-main">\n' +
                '                            <div class="comment-user text-small">\n' +
                '                                <span class="reply_nickname text-muted">{1}</span>\n' +
                '                                <span class="to_nickname text-muted">{2}</span>\n' +
                '                            </div>\n' +
                '                            <div class="comment-body">\n' +
                '                                {3}\n' +
                '                            </div>\n' +
                '                            <div class="comment-footer text-muted">\n' +
                '                                <time class="mr-3" >{4}</time>\t\n' +
                '                                <a href="javascript:void(0);" commentId="{5}" id="reply-{5}" class="reply-btn text-muted" onclick="replayComment(this);">回复</a>\t\t\t\n' +
                '                            </div>\n' +
                '                        </div>\t\n' +
                '                    </div>\n' +
                '                </div>\n' +
                '        \n' +
                '                <div class="comment-children-list mr-4 pt-4" >\n' +
                '                    {6}\n' +
                '                </div>';

            // 10、拼接html字符串

            if (parent_comment_id) {  //如果是子评论

                temp = temp.format(
                    data.avatar,
                    data.reply_nickname,
                    '<i class="fa fa-share"></i>' + parent_comment_usename,
                    data.new_content,
                    data.create_time,
                    data.comment_id, "");

                replyDiv.innerHTML += temp;

            } else {
                temp = temp.format(
                    data.avatar,
                    data.reply_nickname,
                    "",
                    data.new_content,
                    data.create_time,
                    data.comment_id, "");

                divComments.innerHTML += temp;

            }

            //改表参与人，评论人数
            var join_human = document.querySelector(".join-humans");
            var join_comment = document.querySelector(".join-comments");
            // console.log(data.add_human);
            join_humans = parseInt(join_human.innerText) + data.add_human;
            join_comments = parseInt(join_comment.innerText) + 1;
            join_human.innerText = join_humans;
            join_comment.innerText = join_comments;

            //关键点, 每次走完此处必须对全局变量清零
            contentArea.value = "";
            parent_comment_id = "";
            parent_comment_usename = "";
            //replyDiv = "";
            // window.location.reload();
            //获取新评论的ip坐标。
            replyBtn = document.getElementById("reply-" + data.comment_id);

            point_top = replyBtn.offsetTop;
            point_left = replyBtn.offsetLeft;
            window.scroll(point_left, point_top); //滚动窗口至文档中的特定位置。

        }

    };

    //请求主体 发送(get请求为空或者写null，post请求数据写在这里，如果没有数据，直接为空或者null)
    //xhr.send(null);
    //post请求发送数据写在send中，key=value&key2=value2
    //console.log('new_content=' + encodeURIComponent(new_content) + '&article_id=' + encodeURIComponent(article_id) + '&parent_id=' + encodeURIComponent(parent_comment_id));
    xhr.send('new_content=' + encodeURIComponent(new_content) + '&parent_id=' + encodeURIComponent(parent_comment_id));
};
}







