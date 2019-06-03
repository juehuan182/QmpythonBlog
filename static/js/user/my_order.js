var wait_timer= null;

function query_payment_result() {
    let order_id = $('.pay-money').parent().attr('order_id');

    let dataParams = {
        'order_id': order_id
    };

    $.post('/shop/order/alipay/check/', dataParams, function (data) {
        console.log(data['code']);
        if (data['code'] === 2) {
            message.showSuccess('支付成功');
            clearInterval(wait_timer);
            // 刷新页面
            location.reload();
        }
    });
}

$('.pay-money').click(function () {
    // 获取订单状态
    let status = $(this).parent().attr('status');
    if (status == 1){
        // 进行支付
        // 获取订单id
        let order_id = $(this).parent().attr('order_id');

        let dataParams = {
            'order_id': order_id
        };

        $.ajax({
            url: '/shop/order/alipay/',
            type: 'POST',
            data: dataParams,
            dataType: 'json',
            success: function (res) {
                if (res['code'] === 2){
                    // 引导客户到我们的支付页面
                    window.open( res['data']['pay_url']);
                    // 调用支付宝交易查询结果, 客户付款可能也要很长事件，所以搞个定时器去执行
                    // setTimeout(query_payment_result(),20000);
                    //wait_timer = setInterval(query_payment_result, 30000);

                }else {
                    clearInterval(wait_timer);
                    message.showError(res['msg']);
                }
            },
            error: function (err) {
                clearInterval(wait_timer);
                message.showError('服务器错误，请重试');

            }
        });
    }else if (status == 4) {
        // 跳转到评价
        window.location.href="/shop/order/comment/";

    }
});
