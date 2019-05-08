let url = "/admin/column/";
// 添加栏目
// 1. 获取按钮
$("#btn-add-column").click(function () {
    var _this = this;
    column_add_or_edit(this);
});

// 编辑新闻标签
// 1. 获取按钮
$(".btn-edit").click(function () {
    var _this = this;
    column_add_or_edit(_this);
});

function column_add_or_edit(_this) {
    //jquery获取data-*属性值还是用attr方式吧，用data可能获取还是之前值，需要处理
    let columnId = $(_this).parents("tr").attr("data-id") ? $(_this).parents("tr").attr("data-id") : 0; //直接用data获取是number型，用val()获取则是string
    let columnName = $(_this).parents("tr").attr("data-name") ? $(_this).parents("tr").attr("data-name") : '';
    let columnLink = $(_this).parents("tr").attr("data-link") ? $(_this).parents("tr").attr("data-link") : '';

    swal({
        title: columnId ? '您正在编辑【' + columnName + '】栏目' : '新增文章栏目',
        text: "栏目名称：<input type='text' name='column-name' id='column-name' value='" + columnName + "'style='width: 70%;display: inline-block'>"
            +"<br/>链接地址：<input type='text' placeholder='请输入链接地址' name='column-link' id='column-link' value='" + columnLink + "'style='width: 70%;display: inline-block'>",
        html:true,
        type: 'input',
        inputValue: columnId ? columnName : '', // 第一个表单元素在这里写才生效，其他在标签内直接写
        inputPlaceholder: '请输入文章栏目名称（20字以内）',
        showCancelButton: true,
        animation: 'slide-from-top',
        closeOnConfirm: false,
        showLoaderOnConfirm: true,
        confirmButtonText: '确定',
        cancelButtonText: '取消'
    }, function () {
        let inputColumnName = $("#column-name").val();
        let inputColumnLink = $("#column-link").val();

        if (!inputColumnName.trim()){
          swal.showInputError("栏目名称不能为空");
          return false;
        }
        if (inputColumnName.length > 20){
          swal.showInputError("栏目名称最长不超过20个字");
          return false;
        }

        if ((columnName && inputColumnName === columnName) && (columnLink && inputColumnLink === columnLink)){
            swal.showInputError("栏目名称和链接地址都未变化，请重新编辑");
            return false;
        }

        var sDataParams = {
            "column_name":inputColumnName,
            "column_link_url": inputColumnLink
        };

        $.ajax({
            // 请求地址
            url: columnId ? url + columnId + "/":url,
            type: columnId ? "PUT":"POST" ,
            data: JSON.stringify(sDataParams),
            // 请求内容的数据类型（前端发给后端格式）
            contentType: "application/json; charset=utf-8",
            // 响应数据的格式（后端返回给前端的格式）
            dataType: "json",
            success: function (res) {
                if (res["code"] === 2) {
                    if(columnId){
                        $(_this).parents('tr').find('td:nth-child(2)').text(inputColumnName);
                        $(_this).parents("tr").attr("data-name",inputColumnName);
                        $(_this).parents('tr').find('td:nth-child(3)').text(inputColumnLink);
                        $(_this).parents("tr").attr("data-link",inputColumnLink);

                        swal({
                            title: "栏目修改成功",
                            text: '',
                            type: "success",
                            showCancelButton: false,
                            showConfirmButton: false,
                            timer: 1500
                        });

                    }else{
                        swal({
                            title: "【" + inputColumnName + "】" + " 栏目添加成功",
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

    let columnId = $(this).parents("tr").attr("data-id");
    let columnName = $(this).parents("tr").attr("data-name");


    swal({
          title: "您确定要删除【" + columnName + "】栏目吗？",
          text: '',
          showCancelButton: true,
          showConfirmButton: true,
          type: "error",
          confirmButtonText: "确认删除",
          cancelButtonText: "取消删除"
        }, function () {
            $.ajax({
                url: url + columnId + "/",   // url尾部需要添加/
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


