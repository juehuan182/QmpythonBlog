$(".btn-del").click(function () {
    let _this = this;
    let commentId = $(this).parents("tr").attr("data-id");

    swal({
            title: "您确定要删除ID为" + commentId + "的评论吗？",
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
                url: '/admin/comments/' + commentId + "/",   // url尾部需要添加/
                type: "DELETE",
                dataType: "json",
                success: function success(res) {
                    if (res['code'] === 2) {
                        swal({
                                title: "评论删除成功",
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


$(".btn-edit").click(function () {
    let _this = this;
    let is_delete = parseInt($(_this).attr('data-delete')); //0表示要去禁用，1表示要去启用
    let comment_id = $(_this).parent().parent().data('id');

    let $this_tr = $(_this).parent().parent();

    let dataParams = {
        'is_delete': is_delete
    };

    swal({
        title: is_delete ? "确定要启用？" : "确定要禁用？",
        text: '',
        showCancelButton: true,
        showConfirmButton: true,
        type: "error",
        confirmButtonText: "确认",
        cancelButtonText: "取消"
    }, function () {

        $.ajax({
            url: '/admin/comments/' + comment_id + '/',
            type: 'PUT',
            data: JSON.stringify(dataParams),
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            cache: false,
            async : false,
            success: function (res) {
                if(res['code'] === 2){
                    if(is_delete){  // 1表示要去启用
                        $(_this).attr('data-delete', '0');
                        $(_this).removeClass('btn-info').addClass('btn-default');
                        $this_tr.find('td:nth-child(6)').text('启用');
                        $(_this).html('<i class="fa fa-lock"></i>&nbsp;禁用');
                    }else{
                        $(_this).attr('data-delete', '1');
                        $(_this).removeClass('btn-default').addClass('btn-info');
                        $this_tr.find('td:nth-child(6)').text('禁用');
                        $(_this).html('<i class="fa fa-unlock-alt"></i>&nbsp;启用');
                    }
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
    });
});