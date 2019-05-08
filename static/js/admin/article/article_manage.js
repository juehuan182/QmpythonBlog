var url = "/admin/article/";

var $startTime = $("input[name=start_time]");
var $endTime = $("input[name=end_time]");

// 控制日历插件
const config = {
    // 自动关闭
    autoclose: true,
    // 日期格式
    format: 'yyyy-mm-dd',
    // 选择语言为中文
    language: 'zh-CN',
    // 优化样式
    showButtonPanel: true,
    // 高亮今天
    todayHighlight: true,
    // 是否在周行的左侧显示周数
    calendarWeeks: true,
    // 清除
    clearBtn: true,
    // 0 ~11，用于选择时间最早能选择什么时候，一般设置网站上线的时候
    startDate: new Date(2018, 1, 1),
    // 今天
    endDate: new Date()
};

$startTime.datepicker(config);
$endTime.datepicker(config);

// 查询
let $articlesSearch = $(".btn-primary");

$articlesSearch.click(function () {

    let start_time = $startTime.val();
    let end_time = $endTime.val();
    let title = $("input[name='title']").val();
    let author_name = $("input[name='author_name']").val();
    let categoryId = $("input[name='category_id']").val();  // 获取当前选中项的value

    $.ajax({
        type: "get",  //  数据发送的方式（post 或者 get）
        url: url,   //  要发送的后台地址
        data: {
            'start_time': start_time,
            'end_time': end_time,
            'title': title,
            'author_name': author_name,
            'category_id': categoryId
        },  //  要发送的数据（参数）格式为{'val1':"1","val2":"2"}
        dataType: 'json',  //  后台处理后返回的数据格式
        success: function success(res) {

        },
        error: function error(err) {
            // message.showError("服务器超时，请重试！");
        }
    });
});


// ================== 删除文章 ================

$(".btn-del").click(function () {   // 2. 点击触发事件
    let _this = this;
    let sArticlesId = $(this).data('article-id');

    swal({
        title: "确定删除这篇文章吗?",
        text: "删除之后，将无法恢复！",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "确定删除",
        cancelButtonText: "取消",
        closeOnConfirm: true,
        animation: 'slide-from-top'
    }, function () {
        $.ajax({
            // 请求地址
            url: url + sArticlesId + "/",  // url尾部需要添加/
            // 请求方式
            type: "DELETE",
            dataType: "json",
            success: function success(res) {
                if (res['code'] === 2) {
                    swal({
                        title: "文章删除成功",
                        text: '',
                        type: "success",
                        showCancelButton: false,
                        showConfirmButton: false,
                        timer: 1500
                    });

                    window.location.reload();

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


// 点击添加文章的按钮跳到文章发布页面
$("#btn-add-article").click(function () {
    　window.location.href = "/admin/article/add/";
    
});