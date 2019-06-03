from django.urls import path

from .views import shop_index, ShoppingCartView, CartAddView, CartEditView, CartInfoView, GoodsCategoryListView, GoodsDetailView, OrderInfoView, \
    OrderAddView, OrderAliPayView, OrderAliPayCheckView, wechatPay

app_name = 'shop'
urlpatterns = [
    # 店铺首页
    path('', shop_index, name='shop_index'),

    #某个种类的商品列表
    path('goods_category/<int:category_id>/', GoodsCategoryListView.as_view(), name='goods_categories'),

    # 商品信息
    path('goods/detail/<int:goods_id>/', GoodsDetailView.as_view(), name='goods_detail'),

    # 购物车
    path('cart/', CartInfoView.as_view(), name='cart_list'),
    path('cart/add/', CartAddView.as_view(), name='cart_add'),
    path('cart/edit/', CartEditView.as_view(), name='cart_edit'),
    path('shoppingcart', ShoppingCartView.as_view(), name='shoppingcart'),

    # 订单信息
    path('order/', OrderInfoView.as_view(), name='order_list'),
    path('order/add/', OrderAddView.as_view(), name='order_add'),
    path('order/edit/', CartEditView.as_view(), name='order_edit'),


    # 支付宝支付
    path('order/alipay/', OrderAliPayView.as_view(), name='alipay'),
    # 支付宝结果查询
    path('order/alipay/check/', OrderAliPayCheckView.as_view(), name='alipay_check'),

    # 微信支付
    path('cart/order/wechatPay/', wechatPay, name='wechatPay'),


]

