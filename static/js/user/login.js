// 生成图片UUID验证码
function generateUUID() {
    var d = new Date().getTime();
    if (window.performance && typeof window.performance.now === "function") {
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
    return uuid;
}

// 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCode() {
    // 1、生成一个图片验证码随机编号 generateUUID()
    // 2、拼接请求url /image_codes/<uuid:image_code_id>/
    let imageCodeUrl = "/verification/graph-code?image_code_uuid=" + generateUUID();
    // 3、修改验证码图片src地址
    $(".validation .captcha-graph-img").attr("src", imageCodeUrl);
}

generateImageCode();  // 生成图像验证码图片

// 刷新图形验证码
$(".validation .captcha-graph-img").click(function () {
    generateImageCode();
});

// js获取url传递参数，js获取url？号后面的参数
function getQueryString(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
    var r = window.location.search.substr(1).match(reg);
    if (r != null) return decodeURI(r[2]);
    return null;
}

/*
* 但当参数中有中文的时候， 就会出现乱码的问题。原来是浏览器默认使用的是 encodeURI 对汉字进行的编码
 * 所以在解码的时候就需要使用decodeURI  而不是 unescape 上面的代码稍微修改下后 就能解决中文乱码的问题了
 */

$(".login-btn").on("click", function (ev) {
    ev.preventDefault(); // 关闭元素默认事件
    let username = $("input[name='username']").val();
    let password = $(" input[ name='password' ] ").val();
    // 获取src的参数值image_code_uuid值
    let image_code_uuid = $(".validation .captcha-graph-img").attr("src").split("?")[1].split("=")[1];
    let image_code_text = $("input[name='graph_captcha']").val().toLowerCase();
    let rememberStatus = $("input[type='checkbox']").is(":checked"); //获取单选框是否勾选

    // 获取URL中的next值
    next = getQueryString("next");
    //如果直接输入登录url的则后面没有next参数值
    if (next == null) {
        next = '/';
    }

    if (username && password && (image_code_text || image_code_text.length != 4)) {
        //认证中
        $('.login').addClass('test'); //倾斜特效

        setTimeout(function () {
            $('.login').addClass('testtwo'); //平移特效
        }, 300);

        setTimeout(function () {
            $('.authent').animate({left: "650px"}, {   //右移动
                easing: 'swing',
                duration: 600,
                queue: false
            });
            $('.authent').animate({opacity: 1}, {   //显示出来
                duration: 200,
                queue: false
            });
        }, 500);

        let dataParams = {
            'username': username,
            'password': password,
            'image_code_uuid': image_code_uuid,
            'image_code_text': image_code_text,
            'remember': rememberStatus
        };
        //点击登录，进行ajax请求
        $.ajax({
            url: '/user/login/',
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            data: JSON.stringify(dataParams),
            success: function (result) {

                setTimeout(function () {
                    $('.authent').animate({left: "400px"}, {   //右移动
                        easing: 'swing',
                        duration: 600,
                        queue: false
                    });
                    $('.authent').animate({opacity: 0}, {   //显示出来
                        duration: 200,
                        queue: false
                    });
                }, 2000);

                setTimeout(function () {

                    $('.authent').hide();
                    $('.login').removeClass('test'); //倾斜特效

                    if (result["code"] === 2) {
                        //登录成功

                        $('.login').removeClass('testtwo').addClass('testhree'); //平移特效

                        $('.login div').fadeOut(100);

                        $('.success').fadeIn(1000);
                        $('.success').html(result["msg"] + "<br><br>欢迎回来“全民python”，一起学习python!");

                        //跳转操作
                        setTimeout(function () {
                            window.location.href = next;
                        }, 3000);

                    } else {
                        $('.login').removeClass('testtwo'); //平移特效
                        message.showError(result["msg"]);

                        // 如果有错误，则自动刷新验证码
                        generateImageCode();

                    }
                }, 2400);
            }
        });

    } else {
        message.showError("请确认是否输入您的账号或密码或验证码");
        // 如果有错误，则自动刷新验证码
        generateImageCode();

        return;
    }

});
