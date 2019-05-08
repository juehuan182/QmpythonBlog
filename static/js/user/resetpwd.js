var stepOneBtn = document.querySelector(".step-one-button");
var emailObj = document.querySelector(".username-email");
var emailVal;

stepOneBtn.onclick = function () {
    email = emailObj.value;

    if (email.trim().length === 0) {
        message.showError("请输入您的邮箱");
    }

    let dataParams = {'email': email};

    $.ajax({
        url: '/user/confirm/',
        type: 'POST',
        dataType: 'json',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(dataParams),
        success: function (result) {
            if (result['code'] === 2) {
                //将第一步相关处理掉
                $(".step-one").hide();
                $(".forget-pw-flow ul li").eq(0).removeClass("active-line active-blue");

                emailVal = result['data']['email'];

                //显示第二步01
                //*号处理几位
                var reg = /(.{3}).+(.{2}@.+)/g;
                var str = result['data']['email'];
                $(".step-two-01 .email-code").text(str.replace(reg, "$1****$2"));

                $(".step-two").show();
                $(".step-two-01").show();
                $(".forget-pw-flow ul li").eq(1).addClass("active-line active-blue");


            } else {
                message.showError(result['msg'])
            }
        }

    });

};

var stepTwoBtn01 = document.querySelector(".step-two-button01");
stepTwoBtn01.onclick = function () {

    //将第二步01隐藏
    $(".step-two-01").hide();

    //显示02
    $(".step-two-02").show();
    //用*处理email几位显示
    var reg = /(.{3}).+(.{2}@.+)/g;
    var str = emailVal;
    $(".step-two-02 .email-code").text(str.replace(reg, "$1****$2"));

    var times = 60;
    var wait_timer;

    $(".zc_yzm").val(times + "s");
    $(".zc_yzm").css({"background": "#e0e2e5", "color": "#333", "box-shadow": "none"});
    $(".zc_yzm").attr("disabled", "true");
    wait_timer = setInterval(SetRemainTime, 1000);

    let dataParams = {'email': emailVal};
    // 发送邮件
    $.ajax({
        url: '/verification/restPwd-code/',
        type: 'POST',
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        data: JSON.stringify(dataParams),
        success: function (result) {
            if (result['code'] != 2) {
                message.showError(result['msg']);
            }
        }

    });

    function SetRemainTime() {
        times--;
        $(".zc_yzm").val(times + "s");
        if (times === 0) {
            clearInterval(wait_timer);
            $(".zc_yzm").css({"background": "#4786ff", "color": "#fff", "box-shadow": "0 0 10px 1px #b5ceff"});
            $(".zc_yzm").removeAttr("disabled");
            $(".zc_yzm").val("获取验证码");
        }
    }

};

//重新获取验证码
$(".zc_yzm").on("click", function () {

    var times = 60;
    var wait_timer;

    $(".zc_yzm").val(times + "s");
    $(".zc_yzm").css({"background": "#e0e2e5", "color": "#333", "box-shadow": "none"});
    $(".zc_yzm").attr("disabled", "true");
    wait_timer = setInterval(SetRemainTime, 1000);

    let dataParams = {'email': emailVal};

    // 发送邮件
    $.ajax({
        url: '/verification/restPwd-code/',
        type: 'POST',
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        data: JSON.stringify(dataParams),
        success: function (result) {
            if (result['code'] != 2) {
                message.showError(result['msg']);
            }
        }

    });

    function SetRemainTime() {
        times--;
        $(".zc_yzm").val(times + "s");
        if (times === 0) {
            clearInterval(wait_timer);
            $(".zc_yzm").css({"background": "#4786ff", "color": "#fff", "box-shadow": "0 0 10px 1px #b5ceff"});
            $(".zc_yzm").removeAttr("disabled");
            $(".zc_yzm").val("获取验证码");
        }
    }

});


var stepTwoBtn02 = document.querySelector(".step-two-button02");
stepTwoBtn02.onclick = function () {
    var verifyCode = document.querySelector(".verify-code").value;

    if (verifyCode.trim().length === 0) {
        message.showError("请输入邮箱收到的验证码！");
        return;
    }

    let dataParams = {'email': emailVal, 'verifyCode': verifyCode};

    $.ajax({
        url: '/user/checkVerifyCode/',
        type: 'POST',
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        data: JSON.stringify(dataParams),

        success: function (result) {
            if (result['code'] === 2) {
                //将第二步相关处理掉
                $(".step-two").hide();
                $(".forget-pw-flow ul li").eq(1).removeClass("active-line active-blue");
                //显示第三步
                $(".email-code").text(result['data']);
                $(".step-three").show();
                $(".forget-pw-flow ul li").eq(2).addClass("active-line active-blue");
            } else {
                message.showError(result['msg']);
            }
        }
    });
};

var stepThreeBtn = document.querySelector(".step-three-button");
stepThreeBtn.onclick = function () {
    var password = $(" input[ name='password' ] ").val();
    var surePassword = $(" input[ name='surePassword' ] ").val();

    if (password.trim().length === 0) {
        message.showError("请输入密码！");
        return;
    }
    if (password != surePassword) {
        message.showError("两次密码不一致！");
        return;
    }

    let dataParams =
    $.ajax({
        url: '/user/resetPwd/',
        type: 'POST',
        dataType: 'json',
        data: {"email": emailVal, "password": password, "surePassword": surePassword},
        success: function (result) {
            if (result['code'] === 2) {
                message.showSuccess(result['msg'] + "2秒后将进入登录页面");
                setTimeout(function () {
                    window.location.href = "/user/login/";
                }, 2000);
            } else {
                message.showError(result['msg']);
            }
        }
    });
};