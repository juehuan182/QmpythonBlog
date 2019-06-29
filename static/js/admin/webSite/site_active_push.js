var placeholder = '示例如下：\n' +
    'http://www.example.com/mip/1.html\n' +
    'http://www.example.com/mip/2.htm\n' +
    'http://www.example.com/mip/3/';

$('textarea').val(placeholder);
$('textarea').focus(function () {
    if ($(this).val() == placeholder) {
        $(this).val('');
    }
});

$('textarea').blur(function () {
    if ($(this).val() == '') {
        $(this).val(placeholder);
    }
});


$('#siteurl-btn-submit').click(function () {
    let urls = $('textarea').val();

    if (!urls.trim() || urls.indexOf("示例如下")>-1){
        swal({
            title: "提交链接不能为空",
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500
        });
        return;
    }

    dataParams = {
        'urls': urls
    };

    $.ajax({
            url: '/admin/website_urls/',
            type: 'POST',
            data: JSON.stringify(dataParams),
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function (res) {

                let success = "成功推送的url条数：" + res.success; // 成功推送的url条数
                let remain = "当天剩余的可推送url条数：" + res.remain; // 当天剩余的可推送url条数
                let not_same_site = res.not_same_site; //由于不是本站url而未处理的url列表
                let not_valid = res.not_valid; //不合法的url列表

                if (typeof(not_same_site) == "undefined"){
                    not_same_site = '';
                }else{
                    not_same_site = "由于不是本站url而未处理的url列表：" + res.not_same_site + '\n';
                }

                if (typeof(not_valid) == "undefined"){
                    not_valid = '';
                }else{
                    not_valid = "不合法的url列表：" + res.not_valid + '\n';
                }

                let message = success  + remain  + not_same_site + not_valid;

                swal({
                    title: "链接提交成功",
                    text: message,
                    type: "success",
                    showCancelButton: false,
                    showConfirmButton: false,
                    timer: 8000
                });


            },
            error: function (err) {
                let object_data = err.responseJSON;
                let error = '错误代码：' + object_data.error  + '\n';
                let message = '错误信息：' + object_data.message;

                let error_msg = error + message;

                swal({
                    title: '链接提交失败',
                    text: error_msg,
                    type: "error",
                    showCancelButton: false,
                    showConfirmButton: false,
                    timer: 8000
                });
            }
        });

});