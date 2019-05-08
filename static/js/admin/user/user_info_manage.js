$(".btn-edit").on('click', function (e) {

    let _this = this;
    let is_active = $(_this).attr('data-active'); // '0' 表示要停用，'1'表示要启用
    let user_id = $(_this).parent().parent().data('id');

    let $this_tr = $(_this).parent().parent();

    let dataParams = {
        'is_active': is_active
    };


    swal({
        title: is_active ? "确定要启用？" : "确定要停用？",
        text: '',
        showCancelButton: true,
        showConfirmButton: true,
        type: "error",
        confirmButtonText: "确认",
        cancelButtonText: "取消"
    }, function () {
        $.ajax({
            url: '/admin/user_info/edit/' + user_id + '/',
            type: 'PUT',
            data: JSON.stringify(dataParams),
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function (res) {
                if(res['code'] === 2){
                    if(is_active === '1'){
                        $(_this).attr('data-active', '0');
                        $(_this).removeClass('btn-default').addClass('btn-info');
                        $(_this).html('<i class="fa fa-lock"></i>&nbsp;停用');
                        $this_tr.find('td:nth-child(8)').text('启用');

                    }else{
                        $(_this).attr('data-active', '1');
                        $(_this).removeClass('btn-info').addClass('btn-default');
                        $(_this).html('<i class="fa fa-unlock-alt"></i>&nbsp;启用');
                         $this_tr.find('td:nth-child(8)').text('停用');
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