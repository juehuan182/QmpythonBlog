/**
 * 知识点：jq选择器
   checkbox复选框
 *  (':checked') 所有被选中的 input 元素,选择器选取所有选中的复选框或单选按钮。
 *  (':checkbox') 所有 type="checkbox" 的 <input> 元素
 *  find():返回匹配元素集合中每个元素的后代。
 *  children():返回匹配元素集合中每个元素的子元素。
 *  parents(): 获得所有祖先元素
 *  parent(): 获得父元素，遍历单层
 *  next():下一个相邻元素
 *  prev():上一个相邻元素
 *  prop() 方法设置或返回被选元素的属性和值。
 *  remove(): 删除包含本身的元素
 *  empty(): 删除子元素，不包含本身
 *
 * */

// 统计一个商品的小计
function update_goods_amount(sku_ul) {
    // 获取商品单价
    let price = sku_ul.find('.col04 span').text();
    // 获取商品数量
    let count = sku_ul.find('.num-show').val();
    // 统计小计
    amount = parseInt(count) * parseFloat(price);
    // 设置商品小计
    sku_ul.find('strong').text(amount.toFixed(2));
}


// 计算被选中的商品总件和总价格
function update_page_info() {
    // 获取所有被选中的商品checkbox
    // 获取所有被选中的商品所在的ul元素
    let total_count = 0;
    let total_price = 0;
    $('.cart-list-item').find(':checked').parents('ul').each(function () {
        // 获取选中对应商品的数目和小计
        let count = $(this).find('.num-show').val();
        let amount = $(this).find('.col06 strong').text();

        // 累加计算商品的总件数和总价格
        count = parseInt(count);
        amount = parseFloat(amount);

        total_count += count;
        total_price += amount ;
    });
    // 设置被选中的商品总件数和总价格
    $('.total-goods').find('span').text(total_count);
    $('.total-price').find('span').text(total_price.toFixed(2));

}

// 商品全选和全不选
$('.select-all').find(':checkbox').change(function () {
    // 获取全选的checkbox的选中状态
    let is_checked = $(this).prop('checked');

    // 遍历商品的对应的checkbox,设置这些checkbox的选中状态和全选的checkbox保持一致
    $('.cart-list-item').find(':checkbox').each(function () {
        $(this).prop('checked', is_checked);
    });

    // 更新页面信息
    update_page_info();
});

// 某个商品checkbox状态发生改变时，设置全选checkbox的状态
$('.cart-list-item').find(':checkbox').change(function () {
    // 获取页面所有商品的数目
    let all_len = $('.cart-list-item').length;
    // 获取页面上被选中的商品数目
    let checked_len = $('.cart-list-item').find(':checked').length;
    let is_checked = true;
    if (checked_len < all_len){
        is_checked = false;
    }

    $('.select-all').find(':checkbox').prop('checked', is_checked);

    // 更新页面信息
    update_page_info();
});


// 商品数量加减
$('.btn-add').click(function () {
    // 获取商品sku_id和数量count
    let sku_id = $(this).next().attr('data-skuId');

    let count = $(this).next().val();
    count = parseInt(count) + 1;

    let paramsData = {
        'sku_id': sku_id,
        'count': count
    };

    let _this = this;

    $.ajax({
        url: '/shop/cart/edit/',
        type: 'PUT',
        data: JSON.stringify(paramsData),
        // 请求内容的数据类型（前端发给后端的格式）
        contentType: "application/json;charset=utf-8",
        // 响应数据的格式（后端返回给前端的格式）
        dataType: "json",
        success: function (res) {
            if (res['code'] === 2){
                // 重新设置商品数目
                $(_this).next().val(count);
                // 更新商品小计
                update_goods_amount($(_this).parents('ul'));

                // 分是否勾选了，统计小计和总价
                // 获取商品对应checkbox的选中状态，如果被选中，更新页面信息
                let is_checked = $(_this).parents('ul').find(':checkbox').prop('checked');
                if (is_checked){
                    update_page_info();
                }


            }else {
                message.showError(res['msg']);
            }
        },
        error: function (err) {
            message.showError('服务器错误，请重试');

        }
    });


});

// 商品数量加减
$('.btn-reduce').click(function () {
    // 获取商品sku_id和数量count
    let sku_id = $(this).prev().attr('data-skuId');

    let count = $(this).prev().val();
    count = parseInt(count) - 1;
    if (count <= 0){
        return;
    }


    let paramsData = {
        'sku_id': sku_id,
        'count': count
    };

    let _this = this;

    $.ajax({
        url: '/shop/cart/edit/',
        type: 'PUT',
        data: JSON.stringify(paramsData),
        // 请求内容的数据类型（前端发给后端的格式）
        contentType: "application/json;charset=utf-8",
        // 响应数据的格式（后端返回给前端的格式）
        dataType: "json",
        success: function (res) {
            if (res['code'] === 2){
                // 重新设置商品数目
                $(_this).prev().val(count);
                // 更新商品小计
                update_goods_amount($(_this).parents('ul'));

                // 分是否勾选了，统计小计和总价
                // 获取商品对应checkbox的选中状态，如果被选中，更新页面信息
                let is_checked = $(_this).parents('ul').find(':checkbox').prop('checked');
                if (is_checked){
                    update_page_info();
                }


            }else {
                message.showError(res['msg']);
            }
        },
        error: function (err) {
            message.showError('服务器错误，请重试');

        }
    });
});

// 记录用户输入之前的数量
let pre_count = 0;
$('.num-show').focus(function () {
    pre_count = $(this).val();
});

// 手工输入购物车商品数量
$('.num-show').blur(function () {
    // 获取商品sku_id和数量count
    let sku_id = $(this).attr('data-skuId');

    let count = $(this).val();
    if (isNaN(count) || count.trim().length ==0 || parseInt(count)<=0){
        //设置商品的数目为用户输入之前的数目
        count = pre_count;
    }

    count = parseInt(count);

    let paramsData = {
        'sku_id': sku_id,
        'count': count
    };

    let _this = this;

    $.ajax({
        url: '/shop/cart/edit/',
        type: 'PUT',
        data: JSON.stringify(paramsData),
        // 请求内容的数据类型（前端发给后端的格式）
        contentType: "application/json;charset=utf-8",
        // 响应数据的格式（后端返回给前端的格式）
        dataType: "json",
        success: function (res) {
            if (res['code'] === 2){
                // 重新设置商品数目
                $(_this).val(count);
                // 更新商品小计
                update_goods_amount($(_this).parents('ul'));

                // 分是否勾选了，统计小计和总价
                // 获取商品对应checkbox的选中状态，如果被选中，更新页面信息
                let is_checked = $(_this).parents('ul').find(':checkbox').prop('checked');
                if (is_checked){
                    update_page_info();
                }

            }else {
                message.showError(res['msg']);
                $(_this).val(pre_count);
            }
        },
        error: function (err) {
            message.showError('服务器错误，请重试');

        }
    });
});


function del_cart(_this) {
    // 获取商品sku_id
    let sku_id = $(_this).parents('ul').find('.num-show').val();

    $.ajax({
        url: '/shop/cart/edit/',
        type: 'DELETE',
        data: JSON.stringify({'sku_id': sku_id}),
        // 请求内容的数据类型（前端发给后端的格式）
        contentType: "application/json;charset=utf-8",
        // 响应数据的格式（后端返回给前端的格式）
        dataType: "json",
        success: function (res) {
            if (res['code'] === 2){
                if (sku_id){
                    // 删除对应商品所在的ul元素
                    $(_this).parents('ul').remove();
                    // 更新页面，下面选择和选择总价
                    // 获取sku_ul中对应商品的被选中状态
                    let is_checked = $(_this).parents('ul').find(':checkbox').prop('checked');
                    // 删除之前如果被选中了，删除之后需要重新更新页面
                    if (is_checked){
                        update_page_info();
                    }
                    // 重新设置购物车数目
                    $('.total-count').children('em').text(res['data']['total_sku']);

                }else {
                    // 删除所有商品
                    $('.cart-list').empty();   // empty删除子元素不包含本身，remove删除包含本身
                    // 重新设置购物车数目
                    $('.total-count').children('em').text(res['data']['total_sku']);
                }
            }else {
                message.showError(res['msg']);

            }
        },
        error: function (err) {
            message.showError('服务器错误，请重试');
        }

    });
}

// 删除购物车
$('.col07 a').click(function () {
    del_cart(this);
});

// 全部删除
$('.clear-all a').click(function () {
    del_cart(this);
});
