var usercenterTab = document.querySelectorAll("div.usercenter-tab>div");
var contentDiv = document.querySelectorAll(".content>div");
var index = 0;
usercenterTab[index].classList.add("tabPaneSelected");
contentDiv[index].style.display = "block";

for (var i = 0; i < usercenterTab.length; i++) {

    usercenterTab[i].setAttribute("selected", i);

    usercenterTab[i].onclick = function () {
        usercenterTab[index].classList.remove("tabPaneSelected");
        contentDiv[index].style.display = "none";

        index = this.getAttribute("selected");

        contentDiv[index].style.display = "block";
        usercenterTab[index].classList.add("tabPaneSelected");

    };
}

//弹出框
$(".shadow").on("click", function () {
    $(".rc_dialog").toggle();  //toggle显示与隐藏状态
});


//图像上传
function selectImg(file) {
    if (!file.files || !file.files[0]) {
        return;
    }
    var reader = new FileReader();
    reader.onload = function (evt) {
        var replaceSrc = evt.target.result;
        //更换cropper的图片
        $('#photo').cropper('replace', replaceSrc, false);//默认false，适应高度，不失真
    };
    reader.readAsDataURL(file.files[0]);
}

//cropper图片裁剪
$('#photo').cropper({
    aspectRatio: 1, //裁剪框的纵横比，默认是不限制的。例如1:1的头像就写1,16:9可写成16/9。
    preview: '.img-preview',//预览视图,预览图的class名
    viewMode: 3, //
    guides: true,  //裁剪框的虚线(九宫格)
    autoCropArea: 1,  //0-1之间的数值，定义自动剪裁区域的大小，默认0.8
    movable: true, //是否允许移动图片
    dragCrop: true,  //是否允许移除当前的剪裁框，并通过拖动来新建一个剪裁框区域
    resizable: true,  //是否允许改变裁剪框的大小
    zoomable: true,  //是否允许缩放图片大小，是否允许放大图像。
    mouseWheelZoom: false,  //是否允许通过鼠标滚轮来缩放图片
    touchDragZoom: true,  //是否允许通过触摸移动来缩放图片
    rotatable: true,  //是否允许旋转图片
    crop: function (e) {
        // 输出结果数据裁剪图像。

    }
});

//dataURL转换为Blob对象
function dataURLtoBlob(dataurl) {
    var arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new Blob([u8arr], {type: mime});
}

//test:
//var blob = dataURLtoBlob('data:text/plain;base64,YWFhYWFhYQ==');


//点击确认后
$("#sureCut").on("click", function () {
    if ($("#photo").attr("src") == null) {
        return false;
    } else {
        var cas = $('#photo').cropper('getCroppedCanvas');//获取被裁剪后的canvas，由于cropper可以得到两种裁剪后图片的数据（即blob和dataURL）
        var base64url = cas.toDataURL('image/png'); //转换为base64地址形式,data:image/png;base64,iVBORw0KG....
        $("#user-photo").prop("src", base64url);//显示为图片的形式

        //将导航栏的头像也随之改变
        $(".head-avatar-img").prop("src", base64url);

        var blob = dataURLtoBlob(base64url);
        //创建一个 FormData
        var formData = new FormData();
        //图片名字,获取当前时间
        var filename = 'user_' + $(".upload-info").data("userid") + '.png';
        //添加数据进入formData
        formData.append("upload_avatar", blob, filename);

        $.ajax({
            url: '/user/uploadAvatar/', // 要上传的地址
            type: 'POST',
            dataType: 'json',
            cache: false,
            data: formData,
            processData: false, // 必须false才会避开JQ对formdata的默认处理
            contentType: false, // 必须false才会自动加上正确的Content-Type
            success: function (result) {
                if (result["code"] === 2) {
                    // 将上传的头像的地址填入，为保证不载入缓存加个随机数
                    $('#user-photo').attr('src', result["data"]["img_url"] + '?t=' + Math.random());
                    //关闭裁剪框
                    closeTailor();
                    message.showSuccess(result['msg'])
                } else {
                    message.showInfo(data.info);
                }
            },
            error: function (err) {
                console.log(err);
            }
        });
    }
});

//关闭裁剪框
function closeTailor() {
    $(".rc_dialog").toggle();
}

//点击取消按钮
$(".btn-close").on("click", function () {
    $(".rc_dialog").toggle();
});


//生日，日期时间插件，执行一个laydate实例
laydate.render({
    elem: '#birthday' //指定元素
});

//点击修改资料保存按钮
$(".change-profile-button").on("click", function () {
    var nick_name = $('input[name="nickname"]').val();
    var sex = $('input[name="sex"]:checked').val();
    var email = $('input[name="email"]').val();
    var mobile = $('input[name="mobile"]').val();
    var qq = $('input[name="qq"]').val();
    var birthday = $('input[name="birthday"]').val();
    var profile = $("#profile").val();


    if (nick_name.trim().length === 0) {
        message.showError('昵称不能为空！');
        return;
    }

    if (nick_name.length < 3 || nick_name.length > 18) {
        message.showError('昵称长度不少于3位，不超过18位！');
        return false;
    }

    if (mobile.length > 0) {
        if (!isMobile(mobile)) {
            message.showError('手机号码格式输入不正确！');
            return false;
        }
    }

    if (qq.length > 0) {
        if (!isQQ(qq)) {
            message.showError('QQ格式输入不正确！');
            return false;
        }
    }

    let dataParams = {
            nick_name: nick_name,
            sex: sex,
            email: email,
            mobile: mobile,
            qq: qq,
            birthday: birthday,
            profile: profile
        };

    $.ajax({
        url: "/user/profile/",
        data: JSON.stringify(dataParams),
        type: 'PUT',
        success: function (result) {
            if (result['code'] === 2) {

                // val()无法更改input标签里的value值,但是页面有修改的效果
                // attr()更改了input标签里的value值,而且页面有修改的效果

                $('input[name="nickname"]').attr('value', result['data']['nickname']);
                $('input[name="sex"]').attr('value', result['data']['sex']);
                $('input[name="email"]').attr('value', result['data']['email']);
                $('input[name="mobile"]').attr('value', result['data']['mobile']);
                $('input[name="qq"]').attr('value', result['data']['qq']);
                $('input[name="birthday"]').attr('value', result['data']['birthday']);
                $('#profile').attr('value', result['data']['profile']);

                message.showSuccess(result['msg']);

            } else {
                message.showError(result['msg']);
            }

        },
        error: function (errorText) {
            console.log(errorText);
        }

    });

});

//修改密码
$(".change-password-button").on("click", function () {
    var password = $('input[name="password"]').val();
    var new_password = $('input[name="new_password"]').val();
    var confirm_password = $('input[name="confirm_password"]').val();

    //检查2个密码是否一致，检查旧密码和新密码是否一致，如果一致则不用修改提示
    if (new_password.length < 6 || new_password.length > 16) {
        message.showError("密码长度至少6位，不超过16位");
        return false;
    }

    if (!checkPassWord(new_password)){
        message.showError("密码必须包含位数字和字母");
        return false;
    }

    if (new_password != confirm_password) {
        message.showError("新密码和确认密码不一致");
        return false;
    }

    if (password === new_password) {
        message.showInfo("旧密码和新密码一致，不需要修改");
        return false;
    }

    let dataParams = {
        'password': password,
        'new_password': new_password,
        'confirm_password': confirm_password
    };

    $.ajax({
        url: '/user/password/',
        data: JSON.stringify(dataParams),
        type: 'PUT',
        success: function (result) {
            if (result['code'] === 2) {
                //清空页面输入框值
                $('input[name="password"]').val('');
                $('input[name="new_password"]').val('');
                $('input[name="confirm_password"]').val('');

                message.showSuccess(result['msg']);
            } else {
                message.showError(result['msg']);
            }
        },
        error: function (errorText) {
            console.log(errorText);
        }

    });
});