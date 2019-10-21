// ================== 上传图片文件至服务器 ================

let $uploadThumbnail=$("#upload-article-thumbnail");
$uploadThumbnail.change(function () {
    // 获取文件
    let file = this.files[0];
    // 创建一个 FormData
    let formData = new FormData();   // FormData对象来发送二进制文件
    // 把文件添加进去
    formData.append("image_file", file); // FormData构造函数提供的append()方法

    // 判断文章分类
    let upload_method = $("#upload-method").val();
    if (!upload_method || upload_method === '0'){
        swal({
          'title': "请选择上传地址!",
          'text': '',
          'type': 'error',
          'showCancelButton': false,
          'showConfirmButton': false,
          'timer': 1500
        });
        return;
    }

    url  = upload_method === '1' ? '/admin/uploadImageToServer/' : '/admin/uploadQiniu/';

    // 发送请求
    $.ajax({
        url: url,
        type: "POST",
        data: formData,
        // 定义文件的传输
        processData: false, // 必须false才会避开JQ对formdata的默认处理
        contentType: false, // 必须false才会自动加上正确的Content-Type
        success: function (res) {
            if (res["code"] === 2){
                swal({
                    title: "图片上传成功",
                    text: '',
                    type: 'success',
                    showCancelButton: false,
                    showConfirmButton: false,
                    timer: 1500
                });
                // 先清除，再将url填充
                $("#article-thumbnail-url").val();
                // console.log(res["data"]["image_url"]);
                $("#article-thumbnail-url").val(res["data"]["image_url"]);
            }else{
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
                title: '服务器错误，请重试！',
                text: '',
                type: "error",
                showCancelButton: false,
                showConfirmButton: false,
                timer: 1500
            });
        }

    });


});


// 自定义标签
$(".add-tag-btn").click(function () {

        swal({
            title: '新增标签',
            text: '<input type="text" name="tag-name" id="tag-name">',
            html:true,
            type: 'prompt',
            inputPlaceholder: '请输入标签名称，长度限制在20位',
            showCancelButton: true,
            animation: 'slide-from-top',
            closeOnConfirm: false,
            showLoaderOnConfirm: true,
            confirmButtonText: '确定',
            cancelButtonText: '取消'
        }, function () {

        let inputVal = $("#tag-name").val();

        if (!inputVal.trim()){
          swal.showInputError("标签不能为空");
          return false;
        }
        if (inputVal.length > 20){
          swal.showInputError("标签名称最长不超过20");
          return false;
        }

        var sDataParams = {
            "tag_name":inputVal
        };

        $.ajax({
            // 请求地址
            url: "/admin/tag/",
            type: "POST",
            data: JSON.stringify(sDataParams),
            // 请求内容的数据类型（前端发给后端格式）
            contentType: "application/json; charset=utf-8",
            // 响应数据的格式（后端返回给前端的格式）
            dataType: "json",
            success: function (res) {
                if (res["code"] === 2) {
                    swal({
                        title: "【" + inputVal + "】" + " 标签添加成功",
                        text: '',
                        type: "success",
                        showCancelButton: false,
                        showConfirmButton: false,
                        timer: 1500
                    });

                    //加入左边选择框
                    $("#article-tag").append("<option value='"+ res['data']['id'] +"' name='"+ inputVal +"' selected>"+inputVal+"</option>");

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
});


// ================== 统计输入框实时字数 ================


// ================== 发布文章 ================
$("#btn-add-article").click(function () {
    //判断文章标题是否为空
    let sTitle = $("#article-title").val();
    if (!sTitle){
        swal({
          'title': "请填写文章标题!",
          'text': '',
          'type': 'error',
          'showCancelButton': false,
          'showConfirmButton': false,
          'timer': 1500
        });
        return;
    }

    //判断文章关键词是否为空
    let sKeywords = $("#article-keywords").val();
    if (!sKeywords){
        swal({
          'title': "请填写文章关键词!",
          'text': '',
          'type': 'error',
          'showCancelButton': false,
          'showConfirmButton': false,
          'timer': 1500
        });
        return;
    }

    //判断文章描述是否为空
    let sDescription = $("#article-description").val();
    // if (!sDescription){
    //     swal({
    //       'title': "请填写文章描述!",
    //       'text': '',
    //       'type': 'error',
    //       'showCancelButton': false,
    //       'showConfirmButton': false,
    //       'timer': 1500
    //     });
    //     return;
    // }

    //判断文章分类
    let sCategoryId = $("#article-category").val();
    if (!sCategoryId || sCategoryId === '0'){
        swal({
          'title': "请选择文章分类!",
          'text': '',
          'type': 'error',
          'showCancelButton': false,
          'showConfirmButton': false,
          'timer': 1500
        });
        return;
    }

    // 文章缩略图
    let sThumbnailUrl = $("#article-thumbnail-url").val();
    // if (!sThumbnailUrl) {
    //   swal({
    //       'title': "请上传文章缩略图或者填写缩略图URL地址!",
    //       'text': '',
    //       'type': 'error',
    //       'showCancelButton': false,
    //       'showConfirmButton': false,
    //       'timer': 1500
    //     });
    //   return;
    // }

    // let sContentHtml = window.editor.txt.html();
    let sContentHtml = $(".editormd-markdown-textarea").val();
    if (!sContentHtml) {
        swal({
          'title': "请填写文章内容!",
          'text': '',
          'type': 'error',
          'showCancelButton': false,
          'showConfirmButton': false,
          'timer': 1500
        });
        return;
    }

    // 标签非必填选项
    let articleTags = $("#article-tag").val(); // ["1", "17"]
    // if (!articleTags) {
    //     swal({
    //       'title': "请填写文章内容!",
    //       'text': '',
    //       'type': 'error',
    //       'showCancelButton': false,
    //       'showConfirmButton': false,
    //       'timer': 1500
    //     });
    //     return;
    // }


    // 获取article_id 存在表示更新，不存在表示发表，因为创建和修改用同一个接口和页面，故通过这个来判断处理
    let articleId = $(this).data("article-id");
    let url = articleId ? '/admin/article/' + articleId + '/' : '/admin/article/add/';
    let dataParams = {
        "title": sTitle,
        "keywords": sKeywords,
        "description": sDescription,
        "category": sCategoryId,
        "content": sContentHtml,
        "cover_img": sThumbnailUrl,
        "tag": articleTags
    };

    $.ajax({
        // 请求地址
        url: url,
        // 请求方式
        type: articleId ? "PUT" : "POST", // 通过文章id三元运算来选择请求方式
        // 请求数据
        data: JSON.stringify(dataParams),  //把一个对象通过stringify之后变成字符串，
        // 请求内容的数据类型（前端发给后端的格式）
        contentType: "application/json; charset=utf-8",
        // 响应数据的格式（后端返回给前端的格式）
        dataType: "json",
        success: function (res) {
            if (res["code"] === 2){
                if (articleId){
                    swal({
                        title: "文章更新成功",
                        text: '跳转到文章管理页',
                        type: "success",
                        showCancelButton: false,
                        showConfirmButton: false,
                        timer: 1500
                    }, function () {
                        window.location.href = '/admin/article/';
                    });

                }else{
                    swal({
                        title: "文章发表成功",
                        text: '跳转到文章管理页',
                        type: "success",
                        showCancelButton: false,
                        showConfirmButton: false,
                        timer: 1500
                    }, function () {
                        window.location.href = '/admin/article/';
                    });
                }
            }else{
                swal({
                    title: res["msg"],
                    text: '',
                    type: "error",
                    showCancelButton: false,
                    showConfirmButton: false,
                    timer: 2000
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


