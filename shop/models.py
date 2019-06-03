from django.db import models
from db.base_model import ModelBase

# Create your models here.


############# 商品模块##############

class GoodsCategory(ModelBase):
    """
    商品分类
    """
    CATEGORY_TYPE = (
        (1, "一级类目"),
        (2, "二级类目"),
        (3, "三级类目")
    )

    name = models.CharField(max_length=30, verbose_name='类别名')
    category_type = models.SmallIntegerField("类目级别", choices=CATEGORY_TYPE, help_text="类目级别")

    class Meta:
        db_table = 'tb_goods_category'
        ordering = ['id']
        verbose_name = '商品类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

'''
SPU是商品信息聚合的最小单位，是一组可复用、易检索的标准化信息的集合，该集合描述了一个产品
iPhone X 可以确定一个产品即为一个SPU。

SKU是指一款商品，每款都有出现一个SKU，便于电商品牌识别商品。
iPhone X 64G 银色 则是一个SKU。
'''


class GoodsSPU(ModelBase):
    """
    商品SPU模型类
    """
    name = models.CharField(max_length=30, verbose_name='商品SPU名称')
    detail = models.TextField(blank=True)

    class Meta:
        db_table = 'tb_goods_spu'
        ordering = ['id']
        verbose_name = '商品SPU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class GoodsSKU(ModelBase):
    """
    商品SKU模型类
    """
    STATUS_CHOICES = (
        (0, '下线'),
        (1, '上线')
    )
    category = models.ForeignKey(GoodsCategory, on_delete=models.CASCADE, verbose_name="商品类目")
    goods_spu = models.ForeignKey(GoodsSPU, on_delete=models.CASCADE, verbose_name="商品SKU")
    name = models.CharField(max_length=30, verbose_name='商品名称')
    desc = models.CharField(max_length=256, verbose_name='商品简介')
    # 这个字段使用 Python 的 decimal.Decimal 元类来保存一个固定精度的十进制数。max_digits 属性可用于设定数字的最大值， decimal_places 属性用于设置小数位数。
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品单价')
    promotion_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品促销价')
    unite = models.CharField(max_length=20, verbose_name='商品单位')
    image = models.URLField(verbose_name='商品图片')
    # PositiveIntegerField 正整数字段
    stock = models.PositiveIntegerField(default=1, verbose_name='商品库存')
    sales = models.IntegerField(default=0, verbose_name='商品销量')
    # 小整数字段，类似于IntegerField，取值范围依赖于数据库特性
    status = models.SmallIntegerField(default=1, choices=STATUS_CHOICES, verbose_name='商品')

    class Meta:
        db_table = 'tb_goods_sku'
        verbose_name = '商品SKU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class GoodsImage(ModelBase):
    """
    商品图片模型类
    """
    image = models.URLField(verbose_name='商品图片路径')
    goods_sku = models.ForeignKey(GoodsSKU, on_delete= models.CASCADE, verbose_name='商品')


    class Meta:
        db_table = 'tb_goods_image'
        verbose_name = '商品图片'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.goods_sku.name


############# 订单模块 ##############
class OrderInfo(ModelBase):
    """
    订单模型类
    """
    PAY_METHOD_CHOICES = (
        (1, '货到付款'),
        (2, '支付宝'),
        (3, '微信支付'),
        (4, '货到付款')
    )

    PAY_STATUS_CHOICES = (
        (1, '待支付'),
        (2, '待发货'),
        (3, '待收货'),
        (4, '待评价'),
        (5, '已完成')
    )

    order_id = models.CharField(primary_key=True, max_length=30, verbose_name='订单编号')
    pay_method = models.SmallIntegerField(choices=PAY_METHOD_CHOICES, default=2, verbose_name='支付方式')
    order_status = models.SmallIntegerField(choices=PAY_STATUS_CHOICES, default=1, verbose_name='订单状态')
    total_count = models.IntegerField(default=1, verbose_name='产品数量')
    total_price = models.IntegerField(default=1, verbose_name='总价格')
    transit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='运费')

    user = models.ForeignKey('user.Account', on_delete= models.CASCADE,verbose_name='用户')
    address = models.ForeignKey('user.AccountAddress', on_delete= models.CASCADE,verbose_name='地址')

    # 支付宝交易号
    trade_no = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='支付编号')
    # 微信支付会用到
    nonce_str = models.CharField(max_length=50, null=True, blank=True, unique=True, verbose_name='随机加密串')

    class Meta:
        db_table = 'tb_order_info'
        verbose_name = "订单信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.order_id)


class OrderGoods(ModelBase):
    """
    订单内的商品详情模型
    """
    # 一个订单对应多个商品
    order = models.ForeignKey(OrderInfo, on_delete= models.CASCADE,verbose_name='订单')
    sku = models.ForeignKey(GoodsSKU, on_delete= models.CASCADE,verbose_name='商品SKU')
    count = models.SmallIntegerField(default=1, verbose_name='商品数目')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
    comment = models.CharField(max_length=128, default='', verbose_name='评论')

    class Meta:
        db_table = 'tb_order_goods'
        verbose_name = '商品订单'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.order.order_id

