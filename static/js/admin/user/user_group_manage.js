// 删除
$(".btn-del").click(function () {
    let _this = this;
    //获取用户id
    let user_id = $(_this).parent().parent().data("id");
    let user_name = $(_this).parent().parent().data("name");

        swal({
          title: "您确定要取消用户【" + user_name + "】的角色吗？",
          text: '',
          showCancelButton: true,
          showConfirmButton: true,
          type: "error",
          confirmButtonText: "确认",
          cancelButtonText: "取消"
        }, function () {
            $.ajax({
                url: '/admin/user_group/edit/' + user_id + "/",
                type: "DELETE",
                dataType: 'json',
                success: function (res) {
                    if (res['code'] === 2) {
                        swal({
                            title: "用户角色取消成功",
                            text: '',
                            type: "success",
                            showCancelButton: false,
                            showConfirmButton: false,
                            timer: 1500
                        });

                        $(_this).parent().parent().remove();

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
