function historyDel(_this) {
    let article_id = $(_this).attr('data-articleId') ? $(_this).attr('data-articleId') : 0 ;

    let dataParams = {
        'article_id': article_id
    };
    $.ajax({
        url: '/user/history_del/',
        type: 'DELETE',
        data: JSON.stringify(dataParams),
        // 请求内容的数据类型（前端发给后端格式）
        contentType: "application/json; charset=utf-8",
        // 响应数据的格式（后端返回给前端的格式）
        dataType: "json",
        success: function (res) {
            if (res['code'] === 2){
                if (article_id){
                    message.showSuccess("清除记录成功");
                    $(_this).parents("li").remove();
                }else{
                    message.showSuccess("历史浏览记录全部清除成功");
                    $(".history-list").children().remove();
                }
            }else {
                message.showError(result['msg']);

            }
        },
        error: function (err) {
            message.showError("服务器问题，请重试，谢谢！");
        }
    });
}

// 清除所有历史
$('.cleanhsbtn').click(function () {
     historyDel(this);
});

// 清除某一个记录
$('.history-del').click(function () {
     historyDel(this);
});