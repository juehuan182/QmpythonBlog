let url = "/admin/friendlinks/";
$("#btn-add-friendlink").click(function () {
    friendlink_add_or_edit(this);
});

$(".btn-edit").click(function () {
    friendlink_add_or_edit(this);
});


function friendlink_add_or_edit(_this) {
    //jquery获取data-*属性值还是用attr方式吧，用data可能获取还是之前值，需要处理
    let friendlinkId = $(_this).parents("tr").attr("data-id") ? $(_this).parents("tr").attr("data-id") : 0; //直接用data获取是number型，用val()获取则是string
    let friendlinkName = $(_this).parents("tr").attr("data-name") ? $(_this).parents("tr").attr("data-name") : '';
    let friendlinkUrl = $(_this).parents("tr").attr("data-link") ? $(_this).parents("tr").attr("data-link") : '';

    swal({
        title: friendlinkId ? '您正在编辑【' + friendlinkName + '】友情链接' : '新增友情链接',
        text: "名称：<input type='text' name='friendlink-name' id='friendlink-name' value='" + friendlinkName + "'style='width: 70%;display: inline-block'>"
            +"<br/>链接地址：<input type='text' placeholder='请输入链接地址' name='friendlink-url' id='friendlink-url' value='" + friendlinkUrl + "'style='width: 70%;display: inline-block'>",
        html:true,
        type: 'input',
        inputValue: friendlinkId ? friendlinkName : '', // 第一个表单元素在这里写才生效，其他在标签内直接写
        inputPlaceholder: '请输入友情链接名称（20字以内）',
        showCancelButton: true,
        animation: 'slide-from-top',
        closeOnConfirm: false,
        showLoaderOnConfirm: true,
        confirmButtonText: '确定',
        cancelButtonText: '取消'
    }, function () {
        let inputFriendlinkName = $("#friendlink-name").val();

        if (!inputFriendlinkName.trim()){
          swal.showInputError("友情链接名称不能为空");
          return;
        }
        if (inputFriendlinkName.length > 20){
          swal.showInputError("友情链接名称最长不超过20个字");
          return;
        }

        let inputFriendlinkUrl = $("#friendlink-url").val();
        if (!inputFriendlinkUrl.trim()){
          swal.showInputError("友情链接地址不能为空");
          return;
        }

        if ((friendlinkName && inputFriendlinkName === friendlinkName) && (friendlinkUrl && inputFriendlinkUrl === friendlinkUrl)){
            swal.showInputError("名称和链接地址都未变化，请重新编辑");
            return false;
        }

        var sDataParams = {
            "friendlink_name":inputFriendlinkName,
            "friendlink_url": inputFriendlinkUrl
        };

        $.ajax({
            // 请求地址
            url: friendlinkId ? url + friendlinkId + "/":url,
            type: friendlinkId ? "PUT":"POST" ,
            data: JSON.stringify(sDataParams),
            // 请求内容的数据类型（前端发给后端格式）
            contentType: "application/json; charset=utf-8",
            // 响应数据的格式（后端返回给前端的格式）
            dataType: "json",
            success: function (res) {
                if (res["code"] === 2) {
                    if(friendlinkId){
                        $(_this).parents('tr').find('td:nth-child(2)').text(inputFriendlinkName);
                        $(_this).parents("tr").attr("data-name",inputFriendlinkName);
                        $(_this).parents('tr').find('td:nth-child(3)').text(inputFriendlinkUrl);
                        $(_this).parents("tr").attr("data-link",inputFriendlinkUrl);

                        swal({
                            title: "友情链接修改成功",
                            text: '',
                            type: "success",
                            showCancelButton: false,
                            showConfirmButton: false,
                            timer: 1500
                        });

                    }else{
                        swal({
                            title: "【" + inputFriendlinkName + "】" + " 友情链接添加成功",
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

    let friendlinkId = $(this).parents("tr").attr("data-id");
    let friendlinkName = $(this).parents("tr").attr("data-name");


    swal({
          title: "您确定要删除【" + friendlinkName + "】友情链接吗？",
          text: '',
          showCancelButton: true,
          showConfirmButton: true,
          type: "error",
          confirmButtonText: "确认删除",
          cancelButtonText: "取消删除"
        }, function () {
            $.ajax({
                url: url + friendlinkId + "/",   // url尾部需要添加/
                method: "delete",
                dataType: "json",
                success: function success(res) {
                    // console.log(res);
                    if (res["code"] === 2) {
                        swal({
                            title: "分类删除成功",
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


