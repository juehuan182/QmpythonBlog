var url = "/admin/category/";

//  获取添加按钮
$("#btn-add-category").click(function () {
    // 在jQuery使用ajax后$(this)失效，原因很简单，$(this)指向的是最近调用它的jquery对象，
    // 即$(this)就是表示ajax对象了，解决办法也是很简单，在使用$.ajax({})前将$(this)赋给一个变量后即可在$.ajax({})内使用，
    //let _this = this;
    category_add_or_edit(this);
});

//  获取编辑按钮
$(".btn-edit").click(function () {
    category_add_or_edit(this);
});

function category_add_or_edit(_this) {

    let categoryId = $(_this).parents("tr").attr("data-id") ? $(_this).parents("tr").attr("data-id") : 0;
    let categoryName = $(_this).parents("tr").attr("data-name") ? $(_this).parents("tr").attr("data-name") : '';

    let columnId = $(_this).parents("tr").find('td:nth-child(3)').attr("data-id");
    columnId = columnId ? columnId : 0;

    let columnSelectHtml= "<select name='category-column' id='column-select' class='form-control' style='width: 70%;display: inline-block'>"
                        + "<option value='0'>-- 请选择栏目 --</option>";  // 获取选择菜单元素

    // 首先获取选项值，构造选项字符串
    $.ajax({
        url: "/admin/column/list/",
        type:"GET",
        dataType: "json",
        async:false,
        success: function (res) {
            if (res["code"] ===2){
                let columns = res["data"]["column_list"];
                if (columns && columns.length > 0){
                    columns.forEach(function (one_column) {
                        if (columnId && parseInt(columnId)===one_column.id){
                            var optionContent = `<option value="${one_column.id}" selected>${one_column.name}</option>`;
                        }else{
                            var optionContent = `<option value="${one_column.id}">${one_column.name}</option>`; //js字符串拼接 ·${}
                        }
                        columnSelectHtml += optionContent;
                    });
                    columnSelectHtml += "</select>";
                }
            }

        },
        error: function (err) {
            message.showError('服务器超时，请重试！');
        }
    });

    swal({
      title: categoryId ? '您正在编辑【' + categoryName + '】分类' : '新增文章分类',
      text: "分类名称：<input type='text' name='category-name' id='category-name' style='width: 70%;display: inline-block'>"
            +"<br/>所属栏目："+ columnSelectHtml,
      html:true,
      type: "input",
      inputValue: categoryId ? categoryName : '',
      inputPlaceholder: '请输入文章分类名称',
      showCancelButton: true,
      animation: 'slide-from-top',
      closeOnConfirm: false,
      showLoaderOnConfirm: true,
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    }, function(){

        // console.log("添加或编辑");

        let inputCategoryName = $("#category-name").val() ? $("#category-name").val() : '';
        let inputColumnId = $("#column-select").val();
        // data-id，用data("id")获取是number类型，用val()是字符型
        if (!inputCategoryName.trim()){
            swal.showInputError("分类名称不能为空");
            return false;
        }
        if (inputCategoryName.length > 20){
            swal.showInputError('分类名称最长不超过20');
            return false;
        }
        if (!inputColumnId.trim() || inputColumnId === '0'){
            swal.showInputError('请选择所属栏目');
            return;
        }

        if ((inputCategoryName === categoryName) && (parseInt(inputColumnId) === columnId)){
            swal.showInputError("分类和所属栏目都未变化");
            return false;
        }

        var sDataParams = {
            "categoryName": inputCategoryName,
            "columnId":inputColumnId
        };

        $.ajax({
            // 请求地址
            url: categoryId ? url+categoryId+"/" :url,
            type: categoryId ? "PUT" : "POST" ,
            data: JSON.stringify(sDataParams),
            // 请求内容的数据类型（前端发给后端格式）
            contentType: "application/json; charset=utf-8",
            // 响应数据的格式（后端返回给前端的格式）
            dataType: "json",
            success: function (res) {
                if (res["code"] === 2) {
                    if (categoryId){
                        swal({
                            title: "分类修改成功",
                            text: '',
                            type: "success",
                            showCancelButton: false,
                            showConfirmButton: false,
                            timer: 1500
                        });
                        $(_this).parents('tr').find('td:nth-child(1)').text(inputCategoryName);
                        $(_this).parents("tr").attr("data-name",inputCategoryName);

                        $(_this).parents('tr').find('td:nth-child(3)').attr("data-id",inputColumnId);
                        $(_this).parents('tr').find('td:nth-child(3)').text(res['data']['column'][0].name);
                    }else {
                        swal({
                            title: "分类【" + inputCategoryName + "】" + "添加成功",
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
let $categoryDel = $(".btn-del");
// 2. 点击触发事件
$categoryDel.click(function () {
    var _this = this;

    let categoryId = $(_this).parents("tr").attr("data-id") ? $(_this).parents("tr").attr("data-id") : 0;
    let categoryName = $(_this).parents("tr").attr("data-name") ? $(_this).parents("tr").attr("data-name") : '';

    swal({
          title: "您确定要删除【" + categoryName + "】分类吗？",
          text: '',
          showCancelButton: true,
          showConfirmButton: true,
          type: "error",
          confirmButtonText: "确认删除",
          cancelButtonText: "取消删除"
        }, function () {

        $.ajax({
                url: url + categoryId + "/",   // url尾部需要添加/
                method: "DELETE",
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


