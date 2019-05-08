// 生成富文本编辑器  https://www.kancloud.cn/wangfupeng/wangeditor3/332599
let E = window.wangEditor;
window.editor = new E("#course-outline");
window.editor.create();


let $coverUrlObj = $("#course-cover-url");

// ================== 课程封面图至服务器 ================
let $upload_image_server = $("#upload-image-server");
$upload_image_server.change(function () {
    let file = this.files[0];
    let formData = new FormData();
    formData.append("image_file", file)

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
                    text: '',
                    type: "success",
                    showCancelButton: false,
                    showConfirmButton: false,
                    timer: 1500,
                });

                let sImageUrl = res["data"]["image_url"];
                // 先清除，再将url填充
                $coverUrlObj.val('');
                $coverUrlObj.val(sImageUrl);
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


// ================== 课程封面图至七牛（云存储平台） ================
let $progressImage = $(".progress-image");
QINIU.upload({
    "domain": "http://cdn.qmpython.com/",  // 七牛空间域名
    "uptoken_url": "/admin/uploadToken/",	 // 后台返回 token的地址
    "browse_btn": "upload-image-btn",		// 按钮
    "success": function (up, file, info) {
        let domain = up.getOption('domain');
        let res = JSON.parse(info);
        let filePath = domain + res.key;
        $coverUrlObj.val('');
        $coverUrlObj.val(filePath);
    },
    // 失败
    "error": function (up, err, errTip) {
        // console.log('error');
        // console.log(up);
        // console.log(err);
        // console.log(errTip);
        // console.log('error');
        message.showError(errTip);
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

// ================== 上传课程至百度云 ================
let sdk = baidubce.sdk;
let VodClient = sdk.VodClient;

const config = {
    endpoint: 'http://vod.bj.baidubce.com',	// 默认区域名
    credentials: {
        ak: '59ae8ef595d34d38b8e696e794790f10',	 // 填写你的百度云中ak和sk
        sk: '3eb34ff3577046979d6f60b729a9c3b9'
    }
};

var client = new VodClient(config);

let $videoUrlObj = $("#course-video-url");
let $uploadVideo = $("#upload-video-baidu");
$uploadVideo.change(function () {
    let title = $("#course-title").val();
    if (!title){
        swal({
          'title': "请先填写课程标题之后，再上传视频！",
          'text': '',
          'type': 'error',
          'showCancelButton': false,
          'showConfirmButton': false,
          'timer': 1500,
        });
        return;
    }

    let desc = $("#course-desc").val();
    if (!desc){
        swal({
          'title': "请先填写课程描述之后，再上传视频！",
          'text': '',
          'type': 'error',
          'showCancelButton': false,
          'showConfirmButton': false,
          'timer': 1500,
        });
        return;
    }

    let coverImageUrl = $("#course-cover-url").val();
    if (!coverImageUrl) {
        swal({
          'title': "请先上传课程封面图或者填写URL之后，再上传视频！",
          'text': '',
          'type': 'error',
          'showCancelButton': false,
          'showConfirmButton': false,
          'timer': 1500,
        });
       return;
    }

    let BAIDU_VOD_DOMAIN = 'jc7zff48b8tijqf59za.exp.bcevod.com';	//百度云VOD域名

    let video_file = this.files[0];  // 获取文件
    let video_file_type = video_file.type;

    //  调用百度云VOD接口
    let blob = new Blob([video_file], {type: video_file_type});

    client.createMediaResource(title, desc, blob)
    // Node.js中<data>可以为一个Stream、<pathToFile>；在浏览器中<data>为一个Blob对象
      .then(function (response) {
        // 上传完成
        swal({
            title: "视频上传成功",
            text: '',
            type: "success",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500,
        });
        let sMediaId = response.body.mediaId;
        console.log('媒资ID为：', sMediaId);
        let sVideoUrl = 'http://' + BAIDU_VOD_DOMAIN + '/' + sMediaId + '/' + sMediaId + '.m3u8';
        $videoUrlObj.val('');
        $videoUrlObj.val(sVideoUrl);
      })
      .catch(function (error) {
        console.log(error);   // 上传错误
        swal({
          'title': error,
          'text': '',
          'type': 'error',
          'showCancelButton': false,
          'showConfirmButton': false,
          'timer': 1500,
        });
      });
});

// ================== 发布课程 ================
let $pubBtn = $("#btn-pub-course");
$pubBtn.click(function () {

    let title = $("#course-title").val();
    if (!title){
        swal({
          'title': "请先填写课程标题之后，再上传视频！",
          'text': '',
          'type': 'error',
          'showCancelButton': false,
          'showConfirmButton': false,
          'timer': 1500,
        });
        return;
    }

    let desc = $("#course-desc").val();
    if (!desc){
        swal({
          'title': "请先填写课程描述之后，再上传视频！",
          'text': '',
          'type': 'error',
          'showCancelButton': false,
          'showConfirmButton': false,
          'timer': 1500,
        });
        return;
    }

    let coverImageUrl = $("#course-cover-url").val();
    if (!coverImageUrl) {
        swal({
          'title': "请先上传课程封面图或者填写URL之后，再上传视频！",
          'text': '',
          'type': 'error',
          'showCancelButton': false,
          'showConfirmButton': false,
          'timer': 1500,
        });
       return;
    }

    let video_url = $("#course-video-url").val();
    if (!video_url){
        swal({
          'title': "请上传课程URL地址",
          'text': '',
          'type': 'error',
          'showCancelButton': false,
          'showConfirmButton': false,
          'timer': 1500,
        });
        return;
    }

    let duration = $("#course-duration").val();
    if (!duration){
        swal({
          'title': "请填写课程持续时间",
          'text': '',
          'type': 'error',
          'showCancelButton': false,
          'showConfirmButton': false,
          'timer': 1500,
        });
        return;
    }

    let teacherId = $("#course-teacher").val();
    if (!teacherId || teacherId === '0'){
        swal({
          'title': "请选择课程讲师",
          'text': '',
          'type': 'error',
          'showCancelButton': false,
          'showConfirmButton': false,
          'timer': 1500,
        });
        return;
    }

    let categoryId= $("#course-category").val();
    if (!categoryId || categoryId === '0'){
        swal({
          'title': "请选择课程分类",
          'text': '',
          'type': 'error',
          'showCancelButton': false,
          'showConfirmButton': false,
          'timer': 1500,
        });
        return;
    }

    let outline = window.editor.txt.html();
    if (!outline || outline === '<p><br></p>') {
        swal({
          'title': "请填写课程大纲！",
          'text': '',
          'type': 'error',
          'showCancelButton': false,
          'showConfirmButton': false,
          'timer': 1500,
        });
        return;
    }

    // 获取course_id 存在表示更新，不存在表示发表，因为创建和修改用同一个接口和页面，故通过这个来判断处理
    let courseId = $(this).data("course-id");
    let url = courseId ? "/admin/courses/" + courseId + "/" : "/admin/courses/pub/";
    let courseData = {
        'title': title,
        'desc': desc,
        'cover_url': coverImageUrl,
        'video_url': video_url,
        'duration': duration,
        'teacher': teacherId,
        'category': categoryId,
        'outline': outline
    };

    $.ajax({
        url: url,
        type: courseId ? "PUT" : "POST",
        data: JSON.stringify(courseData),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (res) {
            if (res["code"] === 2){
                if (courseId){
                    swal({
                        title: "课程更新成功",
                        text: '跳转到课程管理页',
                        type: "success",
                        showCancelButton: false,
                        showConfirmButton: false,
                        timer: 1500,
                    }, function () {
                        window.location.href = '/admin/courses/';
                    });
                }else{
                    swal({
                        title: "课程发表成功",
                        text: '跳转到课程管理页',
                        type: "success",
                        showCancelButton: false,
                        showConfirmButton: false,
                        timer: 1500,
                    }, function () {
                        window.location.href = '/admin/courses/';
                    });
                }
            }else{
                swal({
                    title: res["msg"],
                    text: '',
                    type: "error",
                    showCancelButton: false,
                    showConfirmButton: false,
                    timer: 1500,
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
                    timer: 1500,
            });
        }
    });
});
