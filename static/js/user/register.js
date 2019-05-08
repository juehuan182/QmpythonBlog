
// 判断用户是否已注册
var usernameObj = document.querySelector("#username");
usernameObj.addEventListener('blur', function () {
    var username = this.value; // 获取用户名
    if (username.trim().length === 0){
        message.showError("用户名不能为空！");
        return false;
    }

    if (!(/^\w{3,20}$/).test(username)) { // test()方法 判断字符串中是否匹配到正则表达式内容，返回的是boolean值 ( true / false )
        message.showError("请输入3-20个字符的用户名！");
        return false;
    }

    // 发送ajax请求，去后端查询用户名是否存在
    $.ajax({
        url: "/user/checkName/",
        type: "GET",
        data: {'username': username},
        dataType: 'json',
        success: function (res) {
            if (res['code'] === 2){
                message.showSuccess(res['msg']);
            }else{
                message.showError(res['msg']);
          }
        },
        error: function (err) {
            message.showError('服务器超时，请重试！');
        }
    });
});

// 判断用户名是否已经注册


// 邮箱验证逻辑
var emailObj = document.querySelector("#email");
emailObj.addEventListener('blur', function () {
    var email = this.value; // 获取邮箱
    if (email.trim().length === 0){
        message.showError("邮箱不能为空！");
        return false;
    }

    if (!isEmail(email)) {
        message.showError('邮箱格式不正确，请重新输入！');
        return false;
    }

    $.ajax({
        url: '/user/checkEmail/',
        type: "GET",
        data: {'email': email},
        dataType: 'json',
        success: function (res) {
            if (res['code'] === 2){
                message.showSuccess(res['msg']);
            }else{
                message.showError(res['msg']);
          }
        },
        error: function (err) {
            message.showError('服务器超时，请重试！');
        }
    });

});


//密码是否可见，通过设置
var viewPassword = document.querySelector(".view-password");
viewPassword.onclick = function () {

    var passwordObj = document.querySelector(".password-input");
    var iconBg = document.querySelector(".form-group>a>i");

    if (passwordObj.type == "password") {
        iconBg.className = "icon-mimakejian iconfont";
        viewPassword.title = "隐藏密码";
        passwordObj.type = "text";
    } else {
        iconBg.className = "icon-mimabukejian iconfont";
        viewPassword.title = "查看密码";
        passwordObj.type = "password";
    }
};

var yzmBtn = document.querySelector('.zc_yzm');
//发送验证码
yzmBtn.onclick = function () {
    var username = $("input[name='username']").val();
    if (username.trim().length === 0){
        message.showError("用户名不能为空！");
        return false;
    }

    var email = $(" input[ name='email' ]").val();
    if (email.trim().length === 0) {
        message.showError("邮箱不能为空！");
        return;
    }

    if (!isEmail(email)) {
        message.showError('邮箱格式输入不正确！');
        return;
    }

    var password = $(" input[ name='password' ]").val();
    if (password.trim().length === 0) {
        message.showError("请设置密码！");
        return false;
    }
    if (password.length < 8 || password.length > 20) {
        message.showError('密码长度不少于6位，不超过16位！');
        return false;
    }
    if (!checkPassWord(password)) {
        message.showError("密码必须包含位数字和字母");
        return false;
    }

    var times = 60;
    $(this).val(times + "s后可重新发送");
    $(this).css({"background": "#e0e2e5", "color": "#333", "box-shadow": "none"});
    $(this).attr("disabled", "true");

    var wait_timer = setInterval(SetRemainTime, 1000);

    let dataParams = {'username': username, 'email': email};

    $.ajax({
        url: '/verification/email-code/',
        type: 'POST',
        data: JSON.stringify(dataParams),
        dataType: 'json',
        async: false,
        success: function (res) {
            if (res['code'] === 2){
                message.showSuccess(res['msg']);
            }else {
                message.showError(res['msg']);
                clearInterval(wait_timer);
                $(".zc_yzm").css({"background": "#4786ff", "color": "#fff", "box-shadow": "0 0 10px 1px #b5ceff"});
                $(".zc_yzm").removeAttr("disabled");
                $(".zc_yzm").val("重新发送验证码");
            }
        },
        error: function (err) {
            message.showError('服务器超时，请重试！');
        }
    });

    function SetRemainTime() {
        if (times === 0) {
            clearInterval(wait_timer); // 停止计时器
            $(".zc_yzm").css({"background": "#4786ff", "color": "#fff", "box-shadow": "0 0 10px 1px #b5ceff"});
            $(".zc_yzm").removeAttr("disabled"); // 启用按钮
            $(".zc_yzm").val("重新发送验证码");
        }else{
            times--;
            $(".zc_yzm").val(times + "s后可重新发送");
        }
    }
};


//点击注册按钮
var regBtn = document.querySelector(".register-button");
regBtn.addEventListener("click", function (e) {

    e.preventDefault(); //阻止事件默认行为。这里阻止表单的默认提交，使用ajax提交

    var username = $("input[name='username']").val();
    var email = $(" input[ name='email' ]").val();
    var password = $(" input[ name='password' ]").val();
    var email_code_text = $(" input[ name='verifyCode' ] ").val();

    // 第三方登录所需字段值
    var registerType = $("input:hidden[name='hdtype']").val();
    var nickName = $("input:hidden[name='hdnickename']").val();
    var avatarUrl = $("input:hidden[name='hdavatarurl']").val();
    var sex = $("input:hidden[name='hdsex']").val();
    var signature = $("input:hidden[name='hdsignature']").val();
    var openId = $("input:hidden[name='hdopenid']").val();
    var loginType = $("input:hidden[name='hidelogintype']").val();


    if (username.trim().length === 0) {

        message.showError("用户名不能为空！");
        return false;
    }

    if (username.length < 3 || username.length > 20) {
        message.showError("用户名长度不少于3位，不超过20位！");
        return false;
    }


    if (email.trim().length === 0) {
        message.showError("邮箱不能为空！");
        return false;
    }
    if (!isEmail(email)) {
        message.showError('邮箱格式输入不正确！');
        return false;
    }

    if (password.trim().length === 0) {
        message.showError("请设置密码！");
        return false;
    }
    if (password.length < 8 || password.length > 20) {
        message.showError('密码长度不少于8位，不超过20位！');
        return false;
    }
    if (!checkPassWord(password)) {
        message.showError("密码必须包含位数字和字母");
        return false;
    }


    if (email_code_text.trim().length === 0) {
        message.showError("请输入邮箱收到的验证码！");
        return;
    }

    let dataParams = {
            'username': username,
            'email': email,
            'password': password,
            'email_code_text': email_code_text,
            'register_type': registerType,
            'nick_name': nickName,
            'avatar_url': avatarUrl,
            'sex': sex,
            'signature': signature,
            'open_id': openId,
            'login_type': loginType
        };

    $.ajax({
        url: '/user/register/',
        type: 'POST',
        dataType: 'json',
        data: JSON.stringify(dataParams),
        async: false, // 关掉异步功能
        success: function (result) {
            if (result['code'] === 2) {
                $("#register-box").hide();

                if (registerType === "bind") {

                    window.location.href = "/user/bindSuccess/?nick_name=" + nickName +
                        "&avatar_url=" + avatarUrl + "&user_nick_name=" + nickName + "&user_head_img=" + avatarUrl;
                } else {

                    $("#register-success").show();
                    var count_down_time = 60;
                    var loginTimer = setInterval(function () {
                        count_down_time--;
                        $("#register-success p>span").text(count_down_time);

                        if (count_down_time === 0) {
                            // 获取URL中的next值
                            next = getQueryString("next");
                            // 如果直接输入登录url的则后面没有next参数值
                            if (next == null) {
                                next = '/';
                            }
                            //跳转页面
                            window.location.href = next;
                        }
                    }, 1000);
                }

            } else {
                message.showError(result['msg'])
            }

        }
    });
});