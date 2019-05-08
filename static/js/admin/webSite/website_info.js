function upload_image(file, type) {
    // 2. 创建一个FormData
    let formData = new FormData();
    // 3.把文件添加进去
    formData.append('image_file', file);
    // 4. 添加上传类型1 logo or 2 icon
    formData.append('image_type', type);

    // 4. 发送ajax请求
    $.ajax({
        url: '/admin/website_info/upload_image/',
        type: "POST",
        data: formData,
        // 定义文件的传输
        processData: false, // 必须false才会避开JQ对formdata的默认处理
        contentType: false, // 必须false才会自动加上正确的Content-Type
        success: function (res) {
            if (res['code'] === 2){
                swal({
                    title: "图片已更新",
                    text: '',
                    type: "success",
                    showCancelButton: false,
                    showConfirmButton: false,
                    timer: 1500
                });
            }else{
                swal({
                    title: res['msg'],
                    text: '',
                    type: "error",
                    showCancelButton: false,
                    showConfirmButton: false,
                    timer: 1500
                });
            }
        },
        error: function (err) {
            swal({
                title: "服务器错误，请稍后重试！",
                text: '',
                type: "error",
                showCancelButton: false,
                showConfirmButton: false,
                timer: 1500
            });


        }
    });
}


$("#web-logo").change(function () {
    // 1. 获取文件
    let file = this.files[0];
    upload_image(file, 'web-logo');
});


$("#web-login-register-logo").change(function () {
    // 1. 获取文件
    let file = this.files[0];
    upload_image(file, 'web-login-register-logo');
});


$("#web-favicon").change(function () {
    // 1. 获取文件
    let file = this.files[0];
    upload_image(file, 'web-favicon');
});



// 其他信息
$(".btn-edit").click(function(){
	let webName = $("#web-name").val();
    if (!webName.trim()){
        swal({
            title: "请输入网站名称",
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500
        });
        return;
    }

	let webDomainName = $("#web-domainname").val();
	if (!webDomainName.trim()){
        swal({
            title: "请输入网站域名",
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500
        });
        return;
    }

	let indexTitle = $("#index-title").val();
	if (!indexTitle.trim()){
        swal({
            title: "首页标题",
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 2500
        });
        return;
    }

	let metaKeywords = $("#meta-keywords").val();
	if (!indexTitle.trim()){
        swal({
            title: "META关键词",
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500
        });
        return;
    }

	let metaDesc = $("#meta-desc").val();
	if (!metaDesc.trim()){
        swal({
            title: "META描述",
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500
        });
        return;
    }

	let dataParams = {
		'webName': webName,
		'webDomainName': webDomainName,
		'indexTitle': indexTitle,
		'metaKeywords': metaKeywords,
		'metaDesc': metaDesc
	};

	$.ajax({
		url: '/admin/website_info/',
		type: 'POST',
		data: JSON.stringify(dataParams),
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        success: function (res) {
            if (res['code'] === 2){

                // val()无法更改input标签里的value值,但是页面有修改的效果
                // attr()更改了input标签里的value值,而且页面有修改的效果
                $('input[name="web_name"]').attr('value', res['data']['web_name']);
                $('input[name="web_domainname"]').attr('value', res['data']['web_domainname']);
                $('input[name="index_title"]').attr('value', res['data']['web_title']);
                $('#meta-keywords').attr('value', res['data']['web_keywords']);
                $('#meta-desc').attr('value', res['data']['web_desc']);

                swal({
                    title: "网站信息修改成功",
                    text: '',
                    type: "success",
                    showCancelButton: false,
                    showConfirmButton: false,
                    timer: 1500
                });

            }else{
                swal({
                    title: res['msg'],
                    text: '',
                    type: "error",
                    showCancelButton: false,
                    showConfirmButton: false,
                    timer: 1500
                });
            }
        },
        error: function (err) {
            swal({
                title: "服务器错误，请稍后重试！",
                text: '',
                type: "error",
                showCancelButton: false,
                showConfirmButton: false,
                timer: 1500
            });
        }

	});
});

