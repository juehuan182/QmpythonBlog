//先判断有多少个了
$("#advertising-add-btn").click(function () {
    if ($(".advertising-list").find("li").length < 9){ //find() 方法获得当前元素集合中每个元素的后代，通过选择器、jQuery 对象或元素来筛选。
        window.location.href = '/admin/advertising/add/';
    }else {
        swal({
            title: "最多只能添加9个轮播图",
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500
        });
    }

});


// ================== 编辑 ================
let $advertisingUpdate = $(".update-btn");
$advertisingUpdate.click(function () {
    let advertising_id = $(this).data("id");
    window.location.href = "/admin/advertising/" + advertising_id + "/";
});


// ================== 删除 ================
let $bannerDel = $(".delete-btn");
$bannerDel.click(function () {   // 2. 点击触发事件
    let _this = this;
    let advertising_id = $(this).data("id");

    swal({
        title: "确定删除这个广告吗?",
        text: "删除之后，将无法恢复！",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "确定删除",
        cancelButtonText: "取消",
        closeOnConfirm: true,
        animation: 'slide-from-top'
    }, function () {
        $.ajax({
            // 请求地址
            url: "/admin/advertising/" + advertising_id + "/",
            // 请求方式
            type: "DELETE",
            dataType: "json",
            success: function success(res) {
                if (res['code'] === 2) {
                    swal({
                        title: "广告删除成功",
                        text: '',
                        type: "success",
                        showCancelButton: false,
                        showConfirmButton: false,
                        timer: 1500
                    });
                    //$(_this).parent().parent().remove();
                    window.location.reload();

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
            error: function error(err) {
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
