// 添加推荐文章
let $categorySelect= $("#category-select");  // 获取分类元素
let $articleSelect= $("#article-select");  // 获取文章元素
let $priority= $("#priority");  // 获取优先级元素
let $saveBtn= $("#save-btn");  // 获取优先级元素

// 选择文章不同类别，获取相应的文章
$categorySelect.change(function () {
    // 获取当前选中的下拉框的value
    let categoryId = $(this).val();
    if (categoryId === '0'){
        // 如果分类没有选择，则每次切换前移除当前所有新闻（忽略第一个）
        $articleSelect.children('option').remove();
        $articleSelect.append('<option value="0">--请选择文章--</option>');

        return;
    }

    // 根据文章分类id向后端发起get请求
    $.ajax({
        url: '/admin/articlesByCategoryId/?categoryId=' + categoryId,
        type: 'GET',
        dataType: 'json',
        success: function (res) {
            if (res["code"] === 2){

                $articleSelect.children('option').remove();
                $articleSelect.append('<option value="0">--请选择文章--</option>');

                let articles = res['data']['article'];

                if (articles && articles.length > 0){
                    articles.forEach(function (one_article) {
                        let optionContent = "<option value=" + one_article.id + ">" + one_article.title + "</option>";
                        $articleSelect.append(optionContent);
                    });
                }
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
        error:function (err) {
                swal({
                    title: "服务器错误，请稍后重试！",
                    text: '',
                    type: "error",
                    showCancelButton: false,
                    showConfirmButton: false,
                    timer: 1500
                });
        }
    })
    
});


// 点击保存按钮执行的事件
$saveBtn.click(function () {
    // 获取优先级
    let priority = $("#priority").val();
    // 获取下拉框中选中的文章标签id和文章id
    let categoryId = $categorySelect.val();
    let articlesId = $articleSelect.val();
    // console.log(articlesId);
    // 判断是否为 0, 表示在第一个 未选择
    if (categoryId !== '0' && articlesId !== '0' && priority !== '0'){
        let dataParams = {
            "priority": priority,
            "article_id": articlesId
        };
        $.ajax({
            // 请求地址
            url: "/admin/recommendarticle/add/",
            type: "POST",
            data: JSON.stringify(dataParams),
            // 请求内容的数据类型（前端发给后端的格式）
            contentType: "application/json;charset=utf-8",
            // 响应数据的格式（后端返回给前端的格式）
            dataType: "json",
            success: function (res) {
                if (res['code'] === 2){
                    swal({
                        title: "推荐文章添加成功",
                        text: '跳转到推荐文章管理页',
                        type: "success",
                        showCancelButton: false,
                        showConfirmButton: false,
                        timer: 1500
                    }, function () {
                        window.location.href = '/admin/recommendarticle/';
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
                    title: "服务器错误，请稍后重试！",
                    text: '',
                    type: "error",
                    showCancelButton: false,
                    showConfirmButton: false,
                    timer: 1500
                });
            }
        });
    }else{
        swal({
            title: "文章分类、文章以及优先级都要选！",
            text: '',
            type: "error",
            showCancelButton: false,
            showConfirmButton: false,
            timer: 1500
        });
    }
});


// 编辑推荐文章
$editBtn = $(".btn-edit");
$editBtn.click(function () {
    let _this = this;
    let priority = $(this).parent().parent().data("priority");
    let recommendArticleId = $(this).parent().parent().data("id");

    swal({
            title: "您正在编辑推荐文章优先级",
            text: "<input type='text' placeholder='编辑文章推荐优先级' name='recommend-article-priority' id='recommend-article-priority' value="+priority+">",
            html:true,
            type: 'input',
            inputValue: priority,
            inputPlaceholder: '请输入文章优先级',
            showCancelButton: true,
            animation: 'slide-from-top',
            closeOnConfirm: false,
            showLoaderOnConfirm: true,
            confirmButtonText: '确定',
            cancelButtonText: '取消'
        }, function () {
            let inputVal = $("#recommend-article-priority").val();
            if (!inputVal.trim()){
                swal.showInputError("输入框不能为空！");
                return false;
            }

            if (inputVal == priority){
                swal.showInputError("优先级未修改");
                return false;
            }

            if (!$.inArray(inputVal, ['1', '2', '3', '4', '5', '6'])) {
                swal.showInputError('优先级只能取1，2，3，4，5，6中的一个');
                return false;
            }

            let dataParams = {
                "priority": inputVal
            };

            $.ajax({
                url: "/admin/recommendarticle/" + recommendArticleId + "/",
                type: "PUT",
                data: JSON.stringify(dataParams),
                contentType: "application/json;charset=utf-8",
                dataType: "json",
                success: function (res) {
                    if (res["code"] === 2){
                        swal({
                            title: "推荐文章优先级修改成功",
                            text: '跳转到推荐文章管理页',
                            type: "success",
                            showCancelButton: false,
                            showConfirmButton: false,
                            timer: 1500
                        }, function () {
                            window.location.href = '/admin/recommendarticle/';
                        });

                    }else{
                        swal({
                            title: res['msg'],
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


// 删除推荐文章
let $delBtn = $(".btn-del");
$delBtn.click(function () {
    let _this = this;
    // 获取热门文章id
    let recommendArticleId = $(this).parent().parent().data("id");

    swal({
        title: "确定删除这篇推荐文章吗？",
        text: "删除之后，将无法恢复！",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "确定删除",
        cancelButtonText: "取消删除",
        closeOnConfirm: true,
        animation: 'slide-from-top',
    }, function () {
        $.ajax({
            url: "/admin/recommendarticle/" + recommendArticleId + "/",
            type: "DELETE",
            dataType: "json",
            success: function success(res) {
                if (res["code"] === 2){
                    swal({
                        title: "推荐文章删除成功",
                        text: '',
                        type: "success",
                        showCancelButton: false,
                        showConfirmButton: false,
                        timer: 1500
                    });
                    $(_this).parent().parent().remove();
                }else{
                    swal({
                        title: res["msg"],
                        text: '',
                        type: "error",
                        showCancelButton: false,
                        showConfirmButton: false,
                        timer: 1500
                    });                }
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
