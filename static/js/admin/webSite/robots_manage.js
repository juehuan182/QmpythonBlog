$(".btn-add").click(function () {
    // 获取robots协议内容
    let robots_content = $(".robots-textarea").val();
    let dataParams = {
        'robots_content': robots_content
    };

    $.ajax({
        url: '/admin/robots/',
        type: 'POST',
        data: JSON.stringify(dataParams),
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        success: function (res) {
            if (res['code'] === 2){
                swal({
                    title: "rebots已更新",
                    text: '',
                    type: "success",
                    showCancelButton: false,
                    showConfirmButton: false,
                    timer: 1500
                });
            }
        },
        error: function (res) {
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