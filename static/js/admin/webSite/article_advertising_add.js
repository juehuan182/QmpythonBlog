var $endTime = $("input[name=advertising-end-time]");

// 控制日历插件
const config = {
    // 自动关闭
    autoclose: true,
    // 日期格式
    format: 'yyyy-mm-dd',
    // 选择语言为中文
    language: 'zh-CN',
    // 优化样式
    showButtonPanel: true,
    // 高亮今天
    todayHighlight: true,
    // 是否在周行的左侧显示周数
    calendarWeeks: true,
    // 清除
    clearBtn: true,
    // 0 ~11，用于选择时间最早能选择什么时候，一般设置网站上线的时候
    startDate: new Date()
    // 今天
    //endDate: new Date()
};

$endTime.datepicker(config);



let $imageUrlObj = $("#advertising-image-url");

// ================== 上传图片至服务器 ================
$("#upload-image-server").change(function () {
    // 获取文件
    let file = this.files[0];
    // 创建一个 FormData
    let formData = new FormData();
    // 把文件添加进去
    formData.append("image_file", file);

    // 发送请求
    $.ajax({
        url: "/admin/uploadImageToServer/",
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
                $("#advertising-image-url").val();
                $("#advertising-image-url").val(res["data"]["image_url"]);

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

// ================== 上传至七牛（云存储平台） ================
let $progressBar = $(".progress-bar");  // 进度条
QINIU.upload({
    "domain": "http://cdn.qmpython.com/",  // 七牛空间域名
    "uptoken_url": "/admin/uploadToken/",	 // 后台返回 token的地址
    "browse_btn": "upload-image-btn",		// 按钮
    "success": function (up, file, info) {	 // 成功
      let domain = up.getOption('domain');
      let res = JSON.parse(info);
      let filePath = domain + res.key;
      // console.log(filePath);
      $("#advertising-image-url").val('');
      $("#advertising-image-url").val(filePath);
    },
    "error": function (up, err, errTip) {
      // console.log('error');
      // console.log(up);
      // console.log(err);
      // console.log(errTip);
      // console.log('error');
      // message.showError(errTip);
    },
    // 上传文件的过程中 七牛对于 4M 秒传
    "progress": function (up, file) {
      let percent = file.percent;
      $progressBar.parent().css("display", 'block');
      $progressBar.css("width", percent + '%');
      $progressBar.text(parseInt(percent) + '%');
    },
    // 完成后 去掉进度条
    "complete": function () {
      $progressBar.parent().css("display", 'none');
      $progressBar.css("width", '0%');
      $progressBar.text('0%');
    }
  });


let url = "/admin/advertising/";

let $advertisingAdd = $("#btn-add-advertising");
$advertisingAdd.click(function () {
    advertising_add_or_edit(this);
});

function advertising_add_or_edit(_this) {

    let advertisingId = $(_this).data("id");
    advertisingId = advertisingId ? advertisingId : '';

    let name = $("#advertising-name").val();
    if (!name.trim()){
        swal({
            title: "请填写广告名称",
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500
        });
        return;
    }

    let image_url = $imageUrlObj.val();
    if (!image_url.trim()){
        swal({
            title: "请上传广告图片或输入图片URL地址",
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500
        });
        return;
    }

    let link_to = $("#advertising-link-url").val();
    if (!link_to.trim()){
        swal({
            title: "请输入链接地址",
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500
        });
        return;
    }

    let position = $("#advertising-position").val();
    if (position === '0'){
        swal({
            title: "请选择投放位置",
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500
        });
        return;
    }


    let sort = $("#advertising-priority").val();
    if (!sort.trim()){
        swal({
            title: "请输入优先级",
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500
        });
        return;
    }

    let end_time = $("#advertising-end-time").val();
    if (!end_time.trim()){
        swal({
            title: "请选择结束日期",
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500
        });
        return;
    }

    let dataParams = {
        "name": name,
        "image_url": image_url,
        "link_to": link_to,
        "position": position,
        "sort": sort,
        "end_time": end_time
    };

    $.ajax({
        // 请求地址
        url: advertisingId ? url+advertisingId+"/" : url + "add/",
        // 请求方式
        type: advertisingId ? "PUT" : "POST",
        // 请求数据
        data: JSON.stringify(dataParams),
        // 请求内容的数据类型（前端发给后端的格式）
        contentType: "application/json; charset=utf-8",
        // 响应数据的格式（后端返回给前端的格式）
        dataType: "json",
        success: function (res) {
            if (res["code"] === 2){
                swal({
                    title: "广告修改成功",
                    text: '跳转到广告管理页',
                    type: 'success',
                    showCancelButton: false,
                    showConfirmButton: false,
                    timer: 1500
                },function () {
                    window.location.href = '/admin/advertising/';
                });
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
                title: "服务器错误，请稍后重试！",
                text: '',
                type: "error",
                showCancelButton: false,
                showConfirmButton: false,
                timer: 1500
            });
        }
    });
};