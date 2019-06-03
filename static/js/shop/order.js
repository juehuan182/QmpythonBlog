update_recevier_address_info();


// 更新寄送地址
function update_recevier_address_info() {
    let addressObj = $('input[name="address_radio"]:checked');
    let name = addressObj.parents('li').find('.addr-name').text();
    let addr = addressObj.parents('li').find('.addr-info').text();
    let tel = addressObj.parents('li').find('.addr-tel').text();

    $('#sendAddr').text('寄送至： ' + addr);
    $('#sendMobile').text('收货人：' + name + ' ' + tel);

}

// 通过选择地址，更新对应寄送地址，checkbox选择触发change事件
$('input[name="address_radio"]').click(function () {
    update_recevier_address_info();
});

// 选择支付方式
$('.payment-list').children('li').click(function () {
    // 添加背景
    $(this).addClass('selected');
    // 去掉其他元素的背景
    $(this).siblings().removeClass('selected');

});

// 提交订单
$('.commit-order > .commit-btn').click(function () {

    // 获取用户选择的地址，支付方式，要购买的商品id字符串
    let addr_id = $('input[name="address_radio"]:checked').val();
    let pay_method = $('.payment-list').children('li.selected').data('pay-method');
    let sku_ids = $(this).attr('sku_ids');

    let paramsData = {
        'addr_id': addr_id,
        'pay_method': pay_method,
        'sku_ids': sku_ids
    };

    $.ajax({
        url: '/shop/order/add/',
        type: 'POST',
        data: JSON.stringify(paramsData),
        // 请求内容的数据类型（前端发给后端的格式）
        contentType: "application/json;charset=utf-8",
        // 响应数据的格式（后端返回给前端的格式）
        dataType: "json",
        success: function (res) {
            if (res['code'] === 2){

                message.showSuccess('提交订单成功');
                //2秒之后跳转到我的订单
                setTimeout(function () {
                    window.location.href = '/user/order/';
                })

            }else {
                message.showError(res['msg']);
            }

        },
        error: function (err) {
                message.showError('服务器错误，请重试');

        }
    });

});