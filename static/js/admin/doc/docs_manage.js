// 删除文档
let $delBtn = $(".btn-del");
$delBtn .click(function () {
    let _this = this;
    // 获取文档id
    let docId = $(this).parents("tr").data("id");
    let docName = $(this).parents("tr").data("name");


    swal({
          title: "您确定要删除【" + docName +"】用户组吗？",
          text: '',
          showCancelButton: true,
          showConfirmButton: true,
          type: "error",
          confirmButtonText: "确认删除",
          cancelButtonText: "取消删除"
        }, function () {
            $.ajax({
                url: "/admin/docs/" + docId + "/",
                type: "DELETE",
                dataType: "json",
                success: function success(res) {
                    if (res["code"] ===2){
                        swal({
                            title: "用户组删除成功",
                            text: '',
                            type: "success",
                            showCancelButton: false,
                            showConfirmButton: false,
                            timer: 1500
                        });
                        $(_this).parent().parent().remove();
                    }else {
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

