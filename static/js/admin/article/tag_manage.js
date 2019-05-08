let url = "/admin/tag/";
// 添加栏目
// 1. 获取按钮
$("#btn-add-tag").click(function () {
    tag_add_or_edit(this);
});

// 编辑新闻标签
// 1. 获取按钮
$(".btn-edit").click(function () {
    tag_add_or_edit(this);
});


function tag_add_or_edit(_this) {

    let tagId = $(_this).parents("tr").attr("data-id") ? $(_this).parents("tr").attr("data-id") : 0; //直接用data获取是number型，用val()获取则是string
    let tagName = $(_this).parents("tr").attr("data-name") ? $(_this).parents("tr").attr("data-name") : '';

    // console.log(tagId,tagName);

    let editHtml = '<input type="text" name="tag-name" id="tag-name" value="' + tagName + '">';
    let addHtml = '<input type="text" name="tag-name" id="tag-name">';

    swal({
        title: tagId ? '您正在编辑【' + tagName + '】标签' : '新增标签',
        text: tagId ? editHtml : addHtml,
        html:true,
        type: 'prompt',
        inputValue: tagName,
        inputPlaceholder: '请输入标签名称，长度限制在20位',
        showCancelButton: true,
        animation: 'slide-from-top',
        closeOnConfirm: false,
        showLoaderOnConfirm: true,
        confirmButtonText: '确定',
        cancelButtonText: '取消'
    }, function () {

        let inputVal = $("#tag-name").val();
        if (tagName && (inputVal === tagName)) {
            swal.showInputError('标签名未变化');
            return false;
        }

        if (!inputVal.trim()){
          swal.showInputError("标签不能为空");
          return false;
        }
        if (inputVal.length > 20){
          swal.showInputError("标签名称最长不超过20");
          return false;
        }

        var sDataParams = {
            "tag_name":inputVal
        };

        $.ajax({
            // 请求地址
            url: tagId ? url + tagId + "/":url,
            type: tagId ? "PUT":"POST" ,
            data: JSON.stringify(sDataParams),
            // 请求内容的数据类型（前端发给后端格式）
            contentType: "application/json; charset=utf-8",
            // 响应数据的格式（后端返回给前端的格式）
            dataType: "json",
            success: function (res) {
                if (res["code"] === 2) {
                    if(tagId){
                        $(_this).parents('tr').find('td:nth-child(2)').text(inputVal);
                        $(_this).parents("tr").attr("data-name",inputVal);

                        swal({
                            title: "标签修改成功",
                            text: '',
                            type: "success",
                            showCancelButton: false,
                            showConfirmButton: false,
                            timer: 1500
                        });

                    }else{
                        swal({
                            title: "【" + inputVal + "】" + " 标签添加成功",
                            text: '',
                            type: "success",
                            showCancelButton: false,
                            showConfirmButton: false,
                            timer: 1500
                        });
                        setTimeout(function () {
                            window.location.reload();
                        }, 1000);
                    }

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
}

// 删除新闻标签
// 1. 获取按钮
// 2. 点击触发事件
$(".btn-del").click(function () {
    var _this = this;

    let tagId = $(this).parents("tr").attr("data-id");
    let tagName = $(this).parents("tr").attr("data-name");


    swal({
          title: "您确定要删除【" + tagName + "】标签吗？",
          text: '',
          showCancelButton: true,
          showConfirmButton: true,
          type: "error",
          confirmButtonText: "确认删除",
          cancelButtonText: "取消删除"
        }, function () {
            $.ajax({
                url: url + tagId + "/",   // url尾部需要添加/
                method: "DELETE",
                dataType: "json",
                success: function success(res) {
                    // console.log(res);
                    if (res["code"] === 2) {
                        swal({
                            title: "标签删除成功",
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


