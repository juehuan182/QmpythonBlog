var bindLoginBtn = document.querySelector(".bind-login-btn");

bindLoginBtn.onclick = function () {

    var username = document.querySelector(".username-input").value;
    var password = document.querySelector(".password-input").value;

    var nickName = document.querySelector(".hide-nickname").value;
    var avatarUrl = document.querySelector(".hide-avatarurl").value;
    var open_id = document.querySelector(".hide-openid").value;
    var login_type = document.querySelector(".hide-logintype").value;

    if (username.trim().length === 0) {

        message.showError("用户名不能为空！");
        return false;
    }

    if (password.trim().length === 0) {

        message.showError("密码不能为空！");
        return false;
    }


    // 创建异步对象
    var xhr = new XMLHttpRequest();
    // 请求行
    xhr.open('post', "/user/bindLogin/");

    // post需要设置请求头header
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded; charset=utf-8");
    // 设置csrf
    var csrftoken = Cookies.get('csrftoken');
    xhr.setRequestHeader("X-CSRFToken", csrftoken);

    // 注册回调函数
    xhr.onreadystatechange = function (ev) {
        if (xhr.readyState == 4 && xhr.status == 200) {

            var result = JSON.parse(xhr.responseText); //由JSON字符串转换为JSON对象

            if (result['code'] === 2) {
                //如果关联成功，那么跳转到成功页面
                window.location.href = "/user/bindSuccess/?nick_name=" + nickName +
                    "&avatar_url=" + avatarUrl + "&user_nick_name=" + result['data']['user_nick_name'] + "&user_head_img=" + result['data']['user_head_img'];
            } else {
                message.showError(result['msg']);
            }
        }
    };

    //发送数据
    xhr.send("username=" + encodeURIComponent(username) + "&password=" + encodeURIComponent(password) + "&open_id=" + encodeURIComponent(open_id)+ "&login_type=" + encodeURIComponent(login_type));

};