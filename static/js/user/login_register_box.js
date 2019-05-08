/*********************登录功能****************************/

// 生成图片UUID验证码, 生成一个图片验证码随机编号
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
    // 2、拼接请求url /image_codes/<uuid:image_code_id>/,用于页面加载时get方式引用
    let image_code_url = "/verification/graph-code?image_code_uuid=" + generateUUID();

    // 3、修改验证码图片src地址
    $(".captcha-graph-img").attr("src", image_code_url);

}

let errorCount=0; //记录错误次数，如果登录三次错误，则需要输入验证码

$(".login").click(function () {
    // 隐藏注册框
    $(".kr-portal").hide();
    $(".kr-passport-register").hide();

    //显示登录框
    $(".kr-portal").show();
    $(".kr-passport-login").show();
    // $(".kr-passport-verifycode").show();
    errorCount=0; //每次弹出登录框清零
});


$(".kr-passport-login .account").blur(function () {
    let _this = this;
    let username = this.value; // 获取用户名

    // 将之前的错误清除
    $(_this).parent('div').removeClass('error');
    $(_this).parent('div').parent('div').find('div:nth-child(2)').remove();

    if (username.trim().length === 0){
        $(_this).parent('div').addClass('error');
        $(_this).parent('div').parent('div').append("<div class='error-area'>请输入用户名或邮箱</div>");
        return;
    }
});

$(".password").blur(function () {

    let _this = this;
    let password = this.value; // 获取用户名

    // 将之前的错误清除
    $(_this).parent('div').removeClass('error');
    $(_this).parent('div').parent('div').find('div:nth-child(2)').remove();

    if (password.trim().length === 0){

        $(_this).parent('div').addClass('error');
        $(_this).parent('div').parent('div').append("<div class='error-area'>请输入密码</div>");
        return;
    }

    if (!checkPassWord(password)) { // test()方法 判断字符串中是否匹配到正则表达式内容，返回的是boolean值 ( true / false )
        $(_this).parent('div').addClass('error');
        $(_this).parent('div').parent('div').append("<div class='error-area'>密码长度为6-16位且必须包含位数字和字母</div>");
    }

});

// 获取验证码
$(".captcha-graph-img").click(function () {
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

var verifycodeObj = '       <div class="kr-passport-verifycode">\n' +
    '        <div class="input-area clearfix ">\n' +
    '         <input type="text" class="code login-code" placeholder="输入验证码"/>\n' +
    '         <div class="send-normal-code ">\n' +
    '            <img class="captcha-graph-img" src="" alt="验证码" title="点击刷新">\n' +
    '         </div>\n' +
    '        </div>\n' +
    '       </div>\n';

$(".kr-passport-login .kr-passport-button").click(function () {
    let username = $(".kr-passport-login .account").val();
    let password = $(".kr-passport-login .password").val();
    let rememberStatus = $("input[type='checkbox']").is(":checked"); //获取单选框是否勾选
    let image_code_uuid = null;
    let image_code_text  = null;
    let dataParams = null;

    // 将之前的错误清除
    $(".login-remember").prev().children().eq(0).removeClass('error');
    $(".login-remember").prev().children().eq(1).remove();

    if (errorCount === 3){
        // 1. 显示验证码
        // $(".kr-passport-verifycode").show();
        $(".kr-passport-password").after(verifycodeObj);
        // 2.生成图像验证码图片
        generateImageCode();
    }

    if (errorCount >= 3){
        // 获取src的参数值image_code_uuid值
        let codeSrc = $(".captcha-graph-img").attr("src");
        image_code_uuid = codeSrc.split("?")[1].split("=")[1];
        image_code_text = $(".kr-passport-login .login-code").val().toLowerCase(); // 这里可能是动态添加的所以不能像用户名和密码一样直接用input获取
    }


    dataParams = {
        'username': username,
        'password': password,
        'image_code_uuid': image_code_uuid,
        'image_code_text': image_code_text,
        'remember': rememberStatus
    };

    // console.log(dataParams);
    //向后台发起ajax请求
    $.ajax({
        url: '/user/login/',
        type: 'POST',
        dataType: 'json',
        data: JSON.stringify(dataParams),
        success: function (res) {
            if (res['code'] === 2){
                window.location.reload();
            }else {

                // $(".login-remember").prev().children(":first").next().remove();
                $(".login-remember").prev().children().eq(0).addClass('error');
                $(".login-remember").prev().append("<div class='error-area'>" + res['msg'] + "</div>");

                errorCount++;
                generateImageCode();
            }
         },
        error: function (err) {
                // $(".login-remember").prev().children(":first").next().remove();
                $(".login-remember").prev().children().eq(0).addClass('error');
                $(".login-remember").prev().append("<div class='error-area'>服务器超时，请重试!</div>");
        }
    });

});

/*********************注册功能****************************/

$(".register").click(function () {
    // 隐藏登录框
    $(".kr-portal").hide();
    $(".kr-passport-login").hide();

    //显示注册框
    $(".kr-portal").show();
    $(".kr-passport-register").show();
});


$(".kr-passport-register .account").blur(function () {
    let _this = this;
    let username = this.value; // 获取用户名

    // 将之前的错误清除
    $(_this).parent('div').removeClass('error');
    $(_this).parent('div').parent('div').find('div:nth-child(2)').remove();

    if (username.trim().length === 0){
        $(_this).parent('div').addClass('error');
        $(_this).parent('div').parent('div').append("<div class='error-area'>请输入用户名</div>");
        return;
    }

    if (!(/^\w{3,20}$/).test(username)) { // test()方法 判断字符串中是否匹配到正则表达式内容，返回的是boolean值 ( true / false )
        $(_this).parent('div').addClass('error');
        $(_this).parent('div').parent('div').append("<div class='error-area'>用户名长度为3-18位</div>");
    }

});


$(".email").blur(function () {
    let _this = this;
    let email = this.value; // 获取邮箱

    // 将之前的错误清除
    $(_this).parent('div').removeClass('error');
    $(_this).parent('div').parent('div').find('div:nth-child(2)').remove();

    if (email.trim().length === 0) {
        $(_this).parent('div').addClass('error');
        $(_this).parent('div').parent('div').append("<div class='error-area'>请输入邮箱</div>");
        return;
    }
    if (!isEmail(email)) {
        $(_this).parent('div').addClass('error');
        $(_this).parent('div').parent('div').append("<div class='error-area'>邮箱格式不正确</div>");
        return;
    }

    // 将发送验证码标签激活
    $(".kr-passport-verifycode .send-normal-code ").addClass('active')

});

var wait_timer = null;
var times = 60;

function SetRemainTime() {
    if (times === 0) {
        clearInterval(wait_timer); // 停止计时器
        $(".kr-passport-register .send-normal-code").addClass('active');
        $(".kr-passport-register .send-normal-code").removeAttr("disabled");
        $(".kr-passport-register .send-normal-code").text("发送验证码");
    }else{
        times--;
        $(".kr-passport-register .send-normal-code").text(times + "s后重发");
    }
}

// 关闭提示框
$(".kr-passport .close").click(function () {
    //隐藏框
    $(".kr-portal").hide();
    $(this).parent().parent().hide();

    //将编辑框输入的置空
    $(" input").val("");

    // 将之前的错误清除
    $("div.input-area").removeClass('error');
    $(".error-area").remove();
    $(".success-area").remove();
    $(".send-normal-code").removeClass("active");

    clearInterval(wait_timer);
    $(".kr-passport-register .send-normal-code").addClass('active');
    $(".kr-passport-register .send-normal-code").removeAttr("disabled");
    $(".kr-passport-register .send-normal-code").text("发送验证码");
});

// 发送验证码
$(".kr-passport-register .send-normal-code").click(function () {

    let _this = this;

    // 将之前的错误清除
    $(this).parent('').removeClass('error');
    $(this).parent('').parent('').children().eq(1).remove();

    let username = $("input[name='account']").val();
    if (username.trim().length === 0){
        $(this).parent('').addClass('error');
        $(this).parent('').parent('').append("<div class='error-area'>请输入用户名</div>");
        return;
    }

    if (!(/^\w{3,20}$/).test(username)) { // test()方法 判断字符串中是否匹配到正则表达式内容，返回的是boolean值 ( true / false )
        $(this).parent('').addClass('error');
        $(this).parent('').parent('').append("<div class='error-area'>用户名长度为3-18位</div>");
        return;

    }

    let email = $(" input[ name='email' ]").val();

    if (email.trim().length === 0) {
        $(this).parent('').addClass('error');
        $(this).parent('').parent('').append("<div class='error-area'>请输入邮箱</div>");
        return;
    }
    if (!isEmail(email)) {
        $(this).parent('').addClass('error');
        $(this).parent('').parent('').append("<div class='error-area'>邮箱格式不正确</div>");
        return;
    }

    let password = $(" input[ name='password' ]").val();
    if (password.trim().length === 0){

        $(this).parent('').addClass('error');
        $(this).parent('').parent('').append("<div class='error-area'>请设置密码</div>");
        return;
    }

    if (!checkPassWord(password)) { // test()方法 判断字符串中是否匹配到正则表达式内容，返回的是boolean值 ( true / false )
        $(this).parent('').addClass('error');
        $(this).parent('').parent('').append("<div class='error-area'>密码长度为6-16位且必须包含位数字和字母</div>");
        return;
    }

    let dataParams = {'username': username, 'email': email};

    wait_timer = setInterval(SetRemainTime, 1000);

    $(_this).text(times + "s后重发");
    $(_this).removeClass('active');
    $(_this).attr("disabled", "true");

   $.ajax({
        url: '/verification/email-code/',
        type: 'POST',
        data: JSON.stringify(dataParams),
        dataType: 'json',
        async: false,
        success: function (res) {
            if (res['code'] === 2){
               $(_this).parent('').parent('').append("<div class='success-area'>验证码已发送您邮箱，3分钟内有效，请注意查收！</div>");
            }else {
                $(_this).parent('').addClass('error');
                $(_this).parent('').parent('').append("<div class='error-area'>"+ res['msg'] +"</div>");

                clearInterval(wait_timer);
                $(_this).addClass('active');
                $(_this).removeAttr("disabled");
                $(_this).text("发送验证码");
            }
        },
        error: function (err) {
            $(_this).parent('').addClass('error');
            $(_this).parent('').parent('').append("<div class='error-area'>服务器超时，请重试</div>");

            clearInterval(wait_timer);
            $(_this).addClass('active');
            $(_this).removeAttr("disabled");
            $(_this).text("发送验证码");

        }
    });

});


// 注册
$(".kr-passport-register .kr-passport-button").click(function () {

    let _this = this;

    // 将之前的错误清除
    $(_this).prev().children().eq(0).removeClass('error');
    $(_this).prev().children().eq(1).remove();

    let username = $("input[name='account']").val();
    if (username.trim().length === 0){
        $(_this).prev().children().eq(0).addClass('error');
        $(_this).prev().append("<div class='error-area'>请输入用户名</div>");
        return;
    }

    if (!(/^\w{3,20}$/).test(username)) { // test()方法 判断字符串中是否匹配到正则表达式内容，返回的是boolean值 ( true / false )
        $(_this).prev().children().eq(0).addClass('error');
        $(_this).prev().append("<div class='error-area'>用户名长度为3-18位</div>");
        return;
    }

    let email = $(" input[ name='email' ]").val();
    if (email.trim().length === 0) {
        $(_this).prev().children().eq(0).addClass('error');
        $(_this).prev().append("<div class='error-area'>请输入邮箱</div>");
        return;
    }
    if (!isEmail(email)) {
        $(_this).prev().children().eq(0).addClass('error');
        $(_this).prev().append("<div class='error-area'>请输入正确格式的邮箱</div>");
        return;
    }

    let password = $("input[ name='password' ]").val();
    if (password.trim().length === 0){
        $(_this).prev().children().eq(0).addClass('error');
        $(_this).prev().append("<div class='error-area'>请设置密码</div>");
        return;
    }

    if (!checkPassWord(password)) { // test()方法 判断字符串中是否匹配到正则表达式内容，返回的是boolean值 ( true / false )
        $(_this).prev().children().eq(0).addClass('error');
        $(_this).prev().append("<div class='error-area'>密码长度为6-16位且必须包含位数字和字母</div>");
        return;
    }

    let email_code_text = $(".register-code").val();
    if (email_code_text.trim().length === 0){
        $(_this).prev().children().eq(0).addClass('error');
        $(_this).prev().append("<div class='error-area'>请输入验证码</div>");
        return;
    }

    if (email_code_text.length != 6){
        $(_this).prev().children().eq(0).addClass('error');
        $(_this).prev().append("<div class='error-area'>注册验证码为6位</div>");
        return;
    }

    let dataParams = {
            'username': username,
            'email': email,
            'password': password,
            'email_code_text': email_code_text
    };

    $.ajax({
        url: '/user/register/',
        type: 'POST',
        // 请求内容的数据类型（前端发给后端的格式）
        contentType: "application/json; charset=utf-8",
        // 响应数据的格式（后端返回给前端的格式）
        dataType: "json",
        data: JSON.stringify(dataParams),
        success: function (res) {
            if (res['code'] === 2){
                window.location.reload();
            }else{
                $(_this).prev().children().eq(0).addClass('error');
                $(_this).prev().append("<div class='error-area'>" + res['msg'] + "</div>");
            }

        },
        error:function (err) {
            $(_this).prev().children().eq(0).addClass('error');
            $(_this).prev().append("<div class='error-area'>服务器超时，请重试!</div>");
        }
    });

});