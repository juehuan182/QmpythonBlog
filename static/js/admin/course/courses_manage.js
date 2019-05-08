// 删除
let $delBtn = $(".btn-del");
$delBtn.click(function () {
    let _this = this;
    let courseId = $(this).parents("tr").data("id");

    $.ajax({
        url: "/admin/courses/" + courseId + "/",
        type: "DELETE",
        dataType: "json",
        success: function (res) {
            if (res["code"] === 2){
                ALERT.alertSuccessToast(res["msg"])
                $(_this).parents("tr").remove();

            }else{
                ALERT.alertErrorToast(res["msg"]);
            }

        },
        error: function (err) {
            message.showError("服务器超时，请重试！");
        }

    });
});


