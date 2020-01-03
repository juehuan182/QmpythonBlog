import logging
from urllib.parse import urlencode
import json
from datetime import datetime
import os

from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django_redis import get_redis_connection
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.conf import settings

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from .models import GoodsCategory, GoodsSKU, OrderGoods, OrderInfo
from user.models import AccountAddress
from util import json_status
from alipay import AliPay  # https://github.com/fzlee/alipay



# Create your views here.

logger = logging.Logger('qmpython')


def shop_index(request):
    """
    显示商铺首页
    """
    # 获取商品种类
    goods_categories = GoodsCategory.objects.all()

    user = request.user
    # 获取购物车商品数目
    cart_count = 0  # 用户没登录就是0

    context = {
        'goods_categories': goods_categories
    }

    return render(request, 'shop/index.html', context=context)


# 购物车
class CartAddView(View):
    def post(self, request):
        '''购物车记录添加'''

        # 此类视图不用min，直接在这判断，因为如果不登陆用了min则直接跳转去了
        if not request.user.is_authenticated:
            return json_status.params_error(message='请先登录')

        # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 数据校验
        if not all([sku_id, count]):
            return json_status.params_error(message='数据不完整')

        # 校验商品数量
        try:
            count = int(count)
        except Exception as e:
            # 数目错误
            return  json_status.params_error(message='商品数目出错')

        # 校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            # 数目错误
            return  json_status.params_error(message='商品不存在')


        # 添加购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_{}'.format(request.user.id)

        # 用hash类型
        # 先尝试获取sku_id的值 ->hget cart_key属性
        # 如果sku_id在hash中不存在,hget返回None
        sku_count =conn.hget(cart_key, sku_id) # 获取sku_id的值， 同一个sku_id有多少数量，属于一个购物车

        if sku_count:
            # 累加购物车中商品sku_id的数目
            count += int(sku_count)

        # 校验商品库存
        if count > sku.stock:
            return json_status.params_error(message='商品库存不足')

        # 设置hash中sku_id对应值
        # hset->如果sku_id已经存在，更新数据，如果sku_id不存在，添加数据
        conn.hset(cart_key, sku_id, count)

        # 计算用户购物车商品的条目数
        cart_count = conn.hlen(cart_key)  # 获取cart_key中多少个sku_id

        return json_status.result(data={'cart_count': cart_count})


class CartInfoView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        conn = get_redis_connection('default')
        conn = get_redis_connection('default')
        cart_key = 'cart_{}'.format(request.user.id)

        # 返回购物车中所有信息
        # hgetall返回哈希表 key 中，所有的域和值。
        cart_dict = conn.hgetall(cart_key)
        #print(cart_dict) # {b'5': b'3', b'3': b'10', b'4': b'1', b'1': b'1'}
        # 遍历获取商品的信息
        sku_list = []
        # 保存用户购物车中商品的总数目和总价格
        total_count = 0
        total_price = 0

        for sku_id, count in cart_dict.items():
            sku = GoodsSKU.objects.get(id=sku_id)
            amount = sku.price * int(count)
            # 动态增加属性
            sku.amount = amount
            sku.count = int(count)
            sku_list.append(sku)

            # 累加计算商品的总数目和总价格
            total_count += int(count)
            total_price += amount

        context = {
            'total_count': total_count,
            'total_price': total_price,
            'sku_list': sku_list,
            'total_sku': len(sku_list) # 统计不同sku数量
        }

        return render(request, 'shop/cart.html', context=context)

# 购物车更新/删除
class CartEditView(View):
    def put(self, request):
        '''购物车记录添加'''

        # 此类视图不用min，直接在这判断，因为如果不登陆用了min则直接跳转去了
        if not request.user.is_authenticated:
            return json_status.params_error(message='请先登录')

        # 接收数据
        # 接收数据
        json_data = request.body
        dict_data = json.loads(json_data.decode('utf-8'))
        sku_id = dict_data.get('sku_id')
        count = dict_data.get('count')

        # 数据校验
        if not all([sku_id, count]):
            return json_status.params_error(message='数据不完整')

        # 校验商品数量
        try:
            count = int(count)
        except Exception as e:
            # 数目错误
            return  json_status.params_error(message='商品数目出错')

        # 校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            # 数目错误
            return  json_status.params_error(message='商品不存在')


        # 添加购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_{}'.format(request.user.id)

        # 校验商品库存
        if count > sku.stock:
            return json_status.params_error(message='商品库存不足')

        conn.hset(cart_key, sku_id, count)

        return json_status.result()


    def delete(self, request):

        if not request.user.is_authenticated:
            return json_status.params_error(message='请先登录')

        # 接收数据
        json_data = request.body
        dict_data = json.loads(json_data.decode('utf-8'))
        sku_id = dict_data.get('sku_id', '')

        # 数据校验
        # if not sku_id:
        #     return json_status.params_error(message='数据不完整')

        # 业务处理，删除购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_{}'.format(request.user.id)
        cart_count = conn.hlen(cart_key)
        if not cart_count:
            json_status.params_error(message='购物车无数据')

        if sku_id:
            # hdel(name,*keys)：将name对应的hash中指定key的键值对删除
            conn.hdel(cart_key, sku_id)
        else:
            # delete(*name) 根据name删除redis中的任意数据类型
            conn.delete(cart_key)

        # 计算用户购物车中商品的总件数{'1': 5, '2':6} ==> 5+6=11
        # total_count = 0
        # vals = conn.hvals(cart_key)
        # for val in vals:
        #     total_count += int(val)

        # 计算sku个数
        total_sku = conn.hlen(cart_key)


        return json_status.result(data={'total_sku': total_sku})


# 使用 django rest framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ShoppingCartView(APIView):
    authentication_classes = []

    def post(self, request):
        '''
            1. 获取数据;
                client_data = request.data
            2. 序列化数据;
                verified_data = ArticleSerializer(data=client_data)

            3. 校验数据;
               if verified_data.is_valid():
                    article = verified_data.save()
                    return Response(verified_data.data)
               else:
                    return Response(verified_data.errors)




        模拟请求数据：
        {
            'sku_id':1,
            'count':2

        }
        Request请求对象：
            REST framework 引入了一个扩展HttpRequest的请求对象，提供了更灵活的请求解析，
            Request对象的核心功能是request.data属性，类似于request.POST，但是对于Web APIs更实用
            request.POST  # 仅可处理表单数据，仅仅用于post请求.
            request.data  # 处理任意数据， 可供 'POST', 'PUT' and 'PATCH' 请求使用.

        Response响应对象：
            REST framework 也引入了一个response对象，它是一种TemplateResponse类型，它渲染文本内容，
            并根据内容决定返回给客户端的数据类型
            return Response(data)  # 通过客户端请求返回渲染的内容
        '''

        # 1. 获取请求数据
        sku_id = request.data.get('sku_id')
        count = request.data.get('count')
        user_id = request.user.pk

        # 2. 校验数据
        if not all([sku_id, count]):
            logging.error('数据不完整')
            return json_status.params_error(message='数据不完整')

        # 校验商品数量
        try:
            count = int(count)
        except Exception as e:
            # 数目错误
            logging.error('商品数目出错')
            return  json_status.params_error(message='商品数目出错')

        # 校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            # 数目错误
            logging.error('商品不存在')
            return  json_status.params_error(message='商品不存在')

        # 添加购物车记录
        '''
            方案1：
            redis={
                cart_key_useid:{
                    {
                        sku: sku1,
                        count:100                    
                    },
                    {
                        sku: sku2,
                        count:200                    
                    },                
                }
            
            }
            这个可以用hash来做，但是嵌套太深
            
            方案2：
            redis={
                cart_user1_sku_1:{
                    {
                        sku: sku1,
                        count:100                    
                    },
                
                },
                
                cart_user1_sku_2:{
                    {
                        sku: sku,
                        count:200                    
                    },
                
                },
            
            }
            可以直接用string实现
        '''

        conn = get_redis_connection('default')
        cart_key = 'cart_{}'.format(user_id)

        # 用hash类型
        # 先尝试获取sku_id的值 ->hget cart_key属性
        # 如果sku_id在hash中不存在,hget返回None
        sku_count =conn.hget(cart_key, sku_id) # 获取sku_id的值， 同一个sku_id有多少数量，属于一个购物车

        if sku_count:
            # 累加购物车中商品sku_id的数目
            count += int(sku_count)

        # 校验商品库存
        if count > sku.stock:
            logging.error('商品库存不足')
            return json_status.params_error(message='商品库存不足')

        # 设置hash中sku_id对应值
        # hset->如果sku_id已经存在，更新数据，如果sku_id不存在，添加数据
        conn.hset(cart_key, sku_id, count)

        # 计算用户购物车商品的条目数
        cart_count = conn.hlen(cart_key)  # 获取cart_key中多少个sku_id

        return Response(data={'cart_count': cart_count})

    def get(self, request):
        '''
            1. 导入模型类；
            2. 创建一个序列化类；
            3. 获取queryset;
            4. 开始序列化；
            5. 获取序列化后的数据，返回给客户端
        '''
        pass








class GoodsCategoryListView(View):
    def get(self, request, category_id):
        category = get_object_or_404(GoodsCategory, pk=category_id)

        skus = GoodsSKU.objects.filter(category=category)

        sort = request.GET.get('sort')
        if sort == 'price':
            skus = skus.order_by('price')
        elif sort == 'hot':
            skus = skus.order_by('-sales')
        else:
            skus = skus.order_by('id')
            sort = 'default'

        # 分页数据
        try:
            page = int(request.GET.get('page', 1))  # 获取页码
        except PageNotAnInteger:
            logger.error("当前页数错误:PageNotAnInteger")
            page = 1

        # 实例化分页对象，articles需要分页的对象，在中间传一个数字，表示每页显示多少个
        paginator = Paginator(skus, settings.ONE_PAGE_COUNT, request=request)
        try:
            skus_info = paginator.page(page)  # 获取当前页的数据
        except EmptyPage:
            # 若访问的页数大于实际页数，则返回最后一页数据
            logger.info("访问的页数大于总页数")
            skus_info = paginator.page(paginator.num_pages)

        other_param = urlencode({
            'sort': sort
        })

        context = {'category': category,
                   'obj_info': skus_info,
                   'sort':sort,
                   'other_param': other_param
                   }

        return render(request, 'shop/goods_category.html', context=context)




class GoodsDetailView(View):
    """
    商品详情
    """
    def get(self, request, goods_id):
        '''显示详情'''
        sku = get_object_or_404(GoodsSKU, pk=goods_id)

        # 获取商品的分类信息
        category = GoodsCategory.objects.all()
        # 获取商品的评论信息
        sku_orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')

        # 获取推荐商品


        # 获取同一SPU的其他规格商品SKU
        same_spu_skus = GoodsSKU.objects.filter(goods_spu=sku.goods_spu).exclude(id=goods_id)

        context = {
            'sku': sku,
            'category': category,
            'sku_orders': sku_orders,
            'same_spu_skus': same_spu_skus
        }


        return render(request, 'shop/goods_detail.html', context=context)




# form表单中被选中的checkbox才会进行提交
class OrderInfoView(View):
    def post(self, request):
        '''提交订单页面'''

        # 获取前端提交的sku_id，form会自动将选中的checkbox值传过来，所以存在多个情况
        sku_ids = request.POST.getlist('sku_id') # ['3', '1', '4', '5']

        # 校验参数
        if not sku_ids:
            return redirect(reverse('shop:cart_list'))

        conn = get_redis_connection('default')
        cart_key = 'cart_{}'.format(request.user.id)

        sku_list = []
        total_count = 0
        total_price = 0
        for sku_id in sku_ids:
            sku = GoodsSKU.objects.get(id=sku_id)
            count = conn.hget(cart_key, sku_id)
            amount = sku.price * int(count)

            # 动态给sku对象增加额外的属性以方便页面查询出来
            sku.count = int(count)
            sku.amount = amount

            sku_list.append(sku)

            # 累加计算商品总数量和商品总价
            total_count += int(count)
            total_price +=amount

        # 运费：实际开发的时候，属于一个子系统，此处我们写死
        transit_price = 10

        # 实付款
        total_pay = total_price + transit_price

        # 获取用户收货地址
        addrs = AccountAddress.objects.filter(user=request.user)

        # 将列表拼接成字符串
        sku_ids = ','.join(sku_ids)

        context = {
            'sku_list': sku_list,
            'total_count': total_count,
            'total_price': total_price,
            'total_pay': total_pay,
            'transit_price': transit_price,
            'addrs': addrs,
            'sku_ids': sku_ids
        }

        return render(request, 'shop/order.html', context=context)




# 前端传递的参数：地址id(addr_id)，支付方式(pay_method) 用户要购买的商品id字符串(sku_ids)
# 用户每下一个订单，就需要向tb_order_info表中加入一条记录。
# 用户的订单中有几个商品，就需要向tb_order_goods表中加入几条记录
'''
mysql事务: 一组sql操作，要么成功，要么都失败.
事务特点: 
原子性：一组事务，要么成功，要么撤回；
稳定性：有非法数据（外键约束之类），事务撤回；
隔离性： 事务独立运行，一个事务处理后的结果，影响了其他事务，那么其他事务会撤回；
可靠性：当出现软件或者硬件崩溃的情况，数据表会驱动日志文件进行重构修改，事务管理语句；

1. 开启一个事务管理 begin
2. 提交操作，对于数据库的操作是永久性的 commit / commit work
3. 回滚会撤销所有未被提交的操作 rollback / rollback work 

事务的隔离级别：
1.读取未被提交的内容（脏读）   read uncommitted 
2.读取提交的内容（数据库默认的隔离级别）  read committed
3.可重复读（易引起幻读）
4.可串行：最高级别，强制事务排序（本质是在每一个读的数据行上加共享锁，可能会带来大量的超时现象和锁竞争）

'''
# 高并发：秒杀
'''
悲观锁：总是假设最坏的情况，每次取数据时都认为其他线程会修改，所以都会加锁（读锁、写锁、行锁等），
       当其他线程想要访问数据时，都需要阻塞挂起。可以依靠数据库实现，如行锁、读锁和写锁等，都是在操作之前加锁。
        
乐观锁：总是认为不会产生并发问题，每次去取数据的时候总认为不会有其他线程对数据进行修改，因此不会上锁，
        但是在更新时会判断其他线程在这之前有没有对数据进行修改。
        
乐观锁其实并不是锁。通过SQL的where子句中的条件是否满足来判断是否满足更新条件来更新数据库，通过受影响行数判断是否更新成功，
如果更新失败可以再次进行尝试，如果多次尝试失败就返回更新失败的结果。

使用乐观锁时，必须设置数据库的隔离级别是Read Committed(可以读到其他线程已提交的数据),这是大多数数据库系统默认隔离级别，但不是MYSQL默认的
如果隔离级别是Repeatable Read(可重复读，读到的数据都是开启事务时刻的数据，即使其他线程提交更新数据，
该线程读取的数据也是之前读到的数据)，乐观锁如果第一次尝试失败,那么不管尝试多少次都会失败。
(Mysql数据库的默认隔离级别是Repeatable Read，需要修改成Read Committed)。

如果是Django2.0以下的版本，需要去修改到这个隔离级别，不然乐观锁操作时无法读取已经被修改的数据

乐观锁：适用于订单并发较少的情况，如果失败次数过多，会带给用户不良体验，同时适用该方法要注意数据库的隔离级别一定要设置为Read Committed 。
最好在使用乐观锁之前查看一下数据库的隔离级别，mysql中查看事物隔离级别的命令为
select @@global.tx_isolation;
修改mysql隔离级别：
vim /etc/mysql/mysql.conf.d/mysqld.cnf
添加  transaction-isolation = REPEATABLE-READ
在并发比较少时建议使用乐观锁,减少加锁、释放锁的开销。在并发比较高的时候，建议使用悲观锁。
如果乐观锁多次尝试的代价比较大，也建议使用悲观锁。
'''
# 支付宝支付

class OrderAddView(View):
    # 开启事务装饰器
    @transaction.atomic
    def post(self, request):
        '''订单创建'''
        user = request.user
        if not user.is_authenticated:
            return json_status.params_error(message='请先登录')

        # 获取参数
        json_data = request.body

        # 校验参数
        if not json_data:
            return json_status.params_error(message='参数错误')

        dict_data = json.loads(json_data.decode('utf-8'))
        addr_id = dict_data.get('addr_id')
        pay_method = dict_data.get('pay_method')
        sku_ids = dict_data.get('sku_ids')

        if not all([addr_id, pay_method, sku_ids]):
            return json_status.params_error(message='数据不完整')

        from collections import OrderedDict  # 创建有序字典
        paymethod_dict = OrderedDict(OrderInfo.PAY_METHOD_CHOICES)

        # 校验支付方式
        if pay_method not in paymethod_dict.keys():  # in 判断key是否存在
            return json_status.params_error(message='非法支付方式')

        # 校验地址
        try:
            addr = AccountAddress.objects.get(id=addr_id)
        except AccountAddress.DoesNotExist:
            return json_status.params_error(message='地址非法')

        # 创建订单核心业务
        # 订单id: 20190510193640+用户id
        order_id = datetime.now().strftime('%Y%m%d%H%M%s')+ str(user.id)
        # 运费
        transit_price = 10

        # 总数目和总金额
        total_count = 0
        total_price = 0

        # 设置事务保存点
        save_id = transaction.savepoint()
        try:

            # 向tb_order_info表中添加一条记录
            order = OrderInfo.objects.create(order_id=order_id,
                                             user=user,
                                             address=addr,
                                             pay_method=pay_method,
                                             total_count=total_count,
                                             total_price=total_price,
                                             transit_price=transit_price)

            # 用户的订单中有几个商品，需要向tb_order_goods表中加入几条记录
            conn = get_redis_connection('default')
            cart_key = 'cart_{}'.format(user.id)

            sku_ids = sku_ids.split(',')  # split 将字符串分割为列表
            for sku_id in sku_ids:
                for i in range(3):
                    # 获取商品的信息
                    try:
                        sku = GoodsSKU.objects.get(id=sku_id) # 不加锁查询
                        # select * from tb_goods_sku where id=sku_id for update; 悲观锁 加互斥锁查询
                        #sku = GoodsSKU.objects.select_for_update().get(id=sku_id)

                    except GoodsSKU.DoesNotExist:
                        # 商品不存在
                        # 回滚事务
                        transaction.savepoint_rollback(save_id)
                        return json_status.params_error(message='商品不存在')

                    # 从redis中获取用户所要购买的商品的数量
                    count = conn.hget(cart_key, sku_id)

                    # 判断商品的库存
                    if int(count) > sku.stock:
                        # 回滚事务
                        transaction.savepoint_rollback(save_id)
                        return json_status.params_error(message='商品库存不足')

                    # 更新商品库存和销量
                    # sku.stock -= int(count)
                    # sku.sales += int(count)
                    # 原库存 (数据库隔离级别必须是Read Committed；如果是Repeatable Read,那么多次尝试读取的原库存都是一样的,读不到其他线程提交更新后的数据。
                    orgin_stock = sku.stock
                    new_stock = orgin_stock - int(count)
                    new_sales = sku.sales + int(count)

                    # update tb_goods_sku set stock=new_stock, sales=new_sales
                    # where id=sku_id and stock = orgin_stock    乐观锁：在更新的时候检查，通过比较更新前后条件
                    # 返回受影响的行数
                    res = GoodsSKU.objects.filter(id=sku_id, stock=orgin_stock).update(stock=new_stock, sales=new_sales)
                    if res == 0:  # 如果更新失败则返回0条记录，说明有问题
                        if i==2:  # 尝试的第三次, range(3)==> 0,1,2
                            transaction.savepoint_rollback(save_id)
                            return json_status.params_error(message='下单失败')
                        continue

                    # 把判断提到前面是防止重复向tb_order_goods表添加记录

                    # 向tb_order_goods表中添加一条记录
                    OrderGoods.objects.create(order_id=order.order_id,
                                              sku=sku,
                                              count=count,
                                              price=sku.price
                                              )


                    # 累加计算订单商品的总数量和总价格
                    amount = sku.price * int(count)
                    total_count += int(count)
                    total_price += amount

                    # 如果执行成功，那直接跳转循环，不用再循环
                    break

            # 更新商品订单信息表中的总数量和总价格， 前面直接设置的为0是为了方便创建订单信息给订单商品使用外键
            order.total_price = total_price
            order.total_count = total_count
            order.save()
        except Exception as e:
            # 回滚事务
            transaction.savepoint_rollback(save_id)
            return json_status.params_error(message='下单失败')

        # 提交事务
        transaction.savepoint_commit(save_id)

        # 清除用户购物车中对应的记录
        conn.hdel(cart_key, *sku_ids) # 将[1,3,4]拆包为1,3,4

        # 返回应答
        return json_status.result()


# !!!!遗留问题：对于事务中抛异常，导致事务回滚异常处理？



# 订单支付
# ajax post
# 前端传递的参数：订单id(order_id)
class OrderAliPayView(View):
    def post(self, request):
        user = request.user
        # 用户是否登录
        if not user.is_authenticated:
            return json_status.params_error(message='请先登录')

        # 接受参数
        order_id = request.POST.get('order_id')

        # 校验参数
        if not order_id:
            return json_status.params_error(message='无效的订单id')

        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          pay_method=2,
                                          order_status=1)

        except OrderInfo.DoesNotExist:
            return json_status.params_error(message='订单错误')

        # 调用支付，使用python sdk调用支付宝的支付接口
        # 使用https://github.com/fzlee/alipay/
        # 初始化
        alipay = AliPay(
            appid="2016092900624781",  # 应用appid
            app_notify_url="http://www.qmpython.com:8000/user/order/notify/",  # 默认回调url
            app_private_key_path=os.path.join(settings.BASE_DIR, 'shop/payment/app_private_key.pem'),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'shop/payment/alipay_public_key.pem'),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False，沙箱环境为True
        )

        # 调用支付接口
        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        total_pay = order.total_price + order.transit_price

        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no= order_id, # 订单id
            total_amount= str(total_pay),  # 支付总金额
            subject= '全民杂货店%s'%order_id,
            return_url= 'http://www.qmpython.com:8000/user/order/return/',  # 同步通知
            notify_url='http://www.qmpython.com:8000/user/order/notify/'  # 异步通知，可选, 不填则使用默认notify url
        )

        #对于PC网站支付的交易，在用户支付完成之后，支付宝会根据API中商户传入的notify_url，
        # 通过POST请求的形式将支付结果作为参数通知到商户系统。


        # 返回应答
        pay_url = "https://openapi.alipaydev.com/gateway.do?" + order_string

        return json_status.result(data={'pay_url': pay_url})


class OrderAliPayCheckView(View):
    def post(self, request):
        user = request.user
        # 用户是否登录
        if not user.is_authenticated:
            return json_status.params_error(message='请先登录')

        # 接受参数
        order_id = request.POST.get('order_id')

        # 校验参数
        if not order_id:
            return json_status.params_error(message='无效的订单id')

        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          pay_method=2,
                                          order_status=1)

        except OrderInfo.DoesNotExist:
            return json_status.params_error(message='订单错误')


        # 调用支付，使用python sdk调用支付宝的支付接口
        # 使用https://github.com/fzlee/alipay/
        # 初始化
        alipay = AliPay(
            appid="2016092900624781",  # 应用appid
            app_notify_url="http://www.qmpython.com:8000/user/order/notify/",  # 默认回调url
            app_private_key_path=os.path.join(settings.BASE_DIR, 'shop/payment/app_private_key.pem'),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'shop/payment/alipay_public_key.pem'),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False，沙箱环境为True
        )


        while True:
            # 调用支付宝查询接口
            result = alipay.api_alipay_trade_query(order_id)
            #print(result)
            code = result.get('code')  # 请求结果
            stauts = result.get('trade_status')  # 支付结果

            #print(code, type(code),stauts)

            if code == '10000' and stauts == 'TRADE_SUCCESS':
                # 支付成功
                # 获取支付宝交易号
                trade_no = result.get('trade_no')
                # 更新订单状态
                order.trade_no = trade_no
                order.order_status = 4  # 待评价
                #order.save()

                #print(order.trade_no)
                #print(order.order_status)

                order.save(update_fields=['trade_no', 'order_status'])
                # 返回结果
                return json_status.result(message='支付成功')

            elif code == '40004' or (code == '10000' and stauts == 'WAIT_BUYER_PAY'):
                # 等待买家付款
                import time
                # 休眠几秒，再次去查询，所以用while循环去调用
                time.sleep(10)
                continue
            else:
                # 支付出错
                return json_status.params_error(message='支付失败')





def wechatPay(request):
    return render(request, 'shop/wechatPay.html')
