
// 计算商品的总价
function update_goods_amount() {
    // 获取商品的单价和数量
    let price = $('.discount-price span').text();
    let count =  $('.num-show').val();
    // 计算商品总价 需要转换为数值
    price = parseFloat(price);
    count = parseInt(count);
    let amount = price * count;
    // 设置商品总价
    $('.goods-total-price').children('span').text(amount.toFixed(2));
}

update_goods_amount();

// 增加商品数量
$('.btn-add').click(function () {
    // 获取商品原有的数目
    let count = $('.choose-amount input').val();
    count = parseInt(count) + 1;

    // 重新设置商品数目
    $('.num-show').val(count);

    // 重新统计总价
    update_goods_amount();

});

// 减少商品数量
$('.btn-reduce').click(function () {
    // 获取商品原有的数目
    let count = $('.choose-amount input').val();
    count = parseInt(count) - 1;
    if (count<=0){
        count=1;
    }
    // 重新设置商品数目
    $('.num-show').val(count);

    // 重新统计总价
    update_goods_amount();

});

// 手动输入商品数量
$('.num-show').blur(function () {
    // 获取商品原有的数目
    let count = $(this).val();
    //校验count是否合法
    if (isNaN(count) || count.trim().length==0 || parseInt(count) <= 0){
        count=1;
    }
    // 重新设置商品数目, 防止用户输入小数，强制转换为整数
    $(this).val(parseInt(count));

    // 重新统计总价
    update_goods_amount();
});


// 添加到购物车
$('.add-cart-btn').click(function () {
    // 获取商品id和商品数量
    let sku_id = $(this).parent().attr('data-skuId');
    let count = $('.num-show').val();

    let paramsData = {
      'sku_id': sku_id,
      'count': count
    };

    $.ajax({
        url: '/shop/cart/add/',
        type: 'POST',
        data: paramsData,
        // 请求内容的数据类型（前端发给后端格式）
        // contentType: "application/json; charset=utf-8",
        // 响应数据的格式（后端返回给前端的格式）
        dataType: "json",
        success: function success(res) {
            if (res["code"] === 2) {
                message.showSuccess('购物车添加成功');
                // 修改购物车数量，注意是购物车数量而不是这个详情里面的数量
                $('#show-count').html(res['data']['cart_count']);

            }else {
                message.showError(res['msg']);
            }

        },
        error: function error(err) {
            message.showError("服务器超时，请重试！");
        }
    })

    ;
});