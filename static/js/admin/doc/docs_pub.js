let $thumbnailUrlObj = $("#doc-thumbnail-url");

// ================== 上传文档缩略图至服务器 ================
let $upload_image_server = $("#upload-image-server");
$upload_image_server.change(function () {
    //console.log(this.files);    // FileList {0: File, length: 1}0: FilelastModified: 1547971695000lastModifiedDate: Sun Jan 20 2019 16:08:15 GMT+0800 (ä¸­å½æ åæ¶é´)name: "fluent_python_1.jpg"size: 18248type: "image/jpeg"webkitRelativePath: ""__proto__: Bloblength: 1__proto__: Object
    let file = this.files[0];  // 获取文件
    let formData = new FormData();  // 创建一个FormData
    formData.append("image_file", file);  // 文件添加进去
    // 发送请求
    $.ajax({
        url: "/admin/uploadImageToServer/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (res) {
            if (res["code"] === 2) {
                swal({
                    title: "图片上传成功",
                    text: "",
                    type: 'success',
                    showCancelButton: false,
                    showConfirmButton: false,
                    timer: 1500
                });

                let sImageUrl = res["data"]["image_url"];
                // 先清除，再将url填充
                $thumbnailUrlObj.val('');
                $thumbnailUrlObj.val(sImageUrl);
            } else {
                swal({
                    title: res["msg"],
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

// ================== 上传文档缩略图至七牛（云存储平台） ================
let $progressImage = $(".progress-image");
QINIU.upload({
    "domain": "http://cdn.qmpython.com/",  // 七牛空间域名
    "uptoken_url": "/admin/uploadToken/",	 // 后台返回 token的地址
    "browse_btn": "upload-image-btn",		// 按钮
    "success": function (up, file, info) {
        let domain = up.getOption('domain');
        let res = JSON.parse(info);
        // console.log(res);
        let filePath = domain + res.key;
        // console.log(filePath);
        $thumbnailUrlObj.val('');
        $thumbnailUrlObj.val(filePath);
    },
    // 失败
    "error": function (up, err, errTip) {
        // console.log('error');
        // console.log(up);
        // console.log(err);
        // console.log(errTip);
        // console.log('error');
        swal({
            title: errTip,
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500
        });


    },
    "progress": function (up, file) {
        let percent = file.percent;
        $progressImage.parent().css("display", 'block');
        $progressImage.css("width", percent + '%');
        $progressImage.text(parseInt(percent) + '%');
    },
    // 完成后 去掉进度条
    "complete": function () {
        $progressImage.parent().css("display", 'none');
        $progressImage.css("width", '0%');
        $progressImage.text('0%');
    }
});

let $docFileUrlObj = $("#doc-file-url");
// ================== 上传文档至服务器 ================
let $upload_file_server = $("#upload-file-server");
$upload_file_server.change(function () {
    let file = this.files[0];  // 获取文件
    let formData = new FormData();  // 创建一个FormData
    formData.append("doc_file", file);  // 文件添加进去
    $.ajax({
        url: "/admin/uploadFileToServer/",
        type: "POST",
        data: formData,
        processData: false,  // 定义文件的传输
        contentType: false,
        success: function (res) {
            if (res["code"] === 2) {
                swal({
                    title: "文件上传成功",
                    text: "",
                    type: 'success',
                    showCancelButton: false,
                    showConfirmButton: false,
                    timer: 1500
                });
                let fileUrl = res.data.file_url;
                $docFileUrlObj.val('');
                $docFileUrlObj.val(fileUrl);
            } else {
                swal({
                    title: res["msg"],
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

// ================== 上传文档至七牛（云存储平台） ================
let $progressFile = $(".progress-file");  // 进度条
QINIU.upload({
    "domain": "http://cdn.qmpython.com/",  // 七牛空间域名
    "uptoken_url": "/admin/uploadToken/",	 // 后台返回 token的地址
    "browse_btn": "upload-file-qiniu",		// 按钮
    // 成功
    "success": function (up, file, info) {
        let domain = up.getOption('domain');
        let res = JSON.parse(info);
        let filePath = domain + res.key;
        console.log(filePath);  // 打印文件路径
        $docFileUrlObj.val('');
        $docFileUrlObj.val(filePath);
    },
    // 失败
    "error": function (up, err, errTip) {
        // console.log('error');
        console.log(up);
        console.log(err);
        console.log(errTip);
        // console.log('error');
        // message.showError(errTip);
        swal({
            title: errTip,
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500
        });
    },
    "progress": function (up, file) {
        let percent = file.percent;
        $progressFile.parent().css("display", 'block');
        $progressFile.css("width", percent + '%');
        $progressFile.text(parseInt(percent) + '%');
    },
    // 完成后 去掉进度条
    "complete": function () {
        $progressFile.parent().css("display", 'none');
        $progressFile.css("width", '0%');
        $progressFile.text('0%');
    }
});

// ================== 发表文档 ================
let $pubBtn = $("#btn-pub-doc");
$pubBtn.click(function () {
    let title = $("#doc-title").val();
    if (!title) {
        swal.showInputError("请填写文档标题!");
        return;
    }

    let thumbnailUrl = $thumbnailUrlObj.val();
    if (!thumbnailUrl) {
        swal.showInputError("请上传文档缩略图或者输入缩略图url!");
        return;
    }

    let docDesc = $("#doc-desc").val();
    if (!docDesc) {
        swal.showInputError("请填写文档描述!");
        return;
    }

    let docFileUrl = $("#doc-file-url").val();
    if (!docFileUrl) {
        swal.showInputError("请上传文档或者输入文档url!");
        return;
    }

    // 获取doc_id 存在表示更新，不存在表示发表，因为创建和修改用同一个接口和页面，故通过这个来判断处理
    let docId = $(this).data("doc-id");
    let url = docId ? "/admin/docs/" + docId + "/" : "/admin/docs/pub/";
    let docData = {
        "title": title,
        "image_url": thumbnailUrl,
        "desc": docDesc,
        "file_url": docFileUrl
    };

    $.ajax({
        url: url,
        type: docId ? "PUT" : "POST",
        data: JSON.stringify(docData),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (res) {
            if (res["code"] === 2) {
                if (docId) {
                    swal({
                        title: "文档更新成功",
                        text: '跳转到文档管理',
                        type: "success",
                        showCancelButton: false,
                        showConfirmButton: false,
                        timer: 1500
                    }, function () {
                        window.location.href = '/admin/docs/';
                    });
                } else {
                    swal({
                        title: "文档发表成功",
                        text: "跳转到文档管理",
                        type: 'success',
                        showCancelButton: false,
                        showConfirmButton: false,
                        timer: 1500
                    },function () {
                        window.location.href = '/admin/docs/';
                    });
                }
            } else {
                swal({
                    title: res["msg"],
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