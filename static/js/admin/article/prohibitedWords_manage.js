$("#upload-prohibitedWords-file").change(function () {
    // 获取文件
    let file = this.files[0];
    // 创建一个 FormData
    let formData = new FormData();
    // 把文件添加进去
    formData.append("words_file", file);

    // 发送请求
    $.ajax({
        url: "/admin/prohibited_words/",
        type: "POST",
        data: formData,
        // 定义文件的传输
        processData: false, // 必须false才会避开JQ对formdata的默认处理
        contentType: false, // 必须false才会自动加上正确的Content-Type
        success: function (res) {
            if (res["code"] === 2){
                swal({
                    title: "文件上传成功",
                    text: '',
                    type: 'success',
                    showCancelButton: false,
                    showConfirmButton: false,
                    timer: 1500
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