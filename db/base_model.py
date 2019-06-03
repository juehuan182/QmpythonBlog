from django.db import models

# 基类
class ModelBase(models.Model):
    """
    """
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间") # 设置为True时，会在model对象第一次被创建时，将字段的值设置为创建时的时间，以后修改对象时，字段的值不会再更新。
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间") # 最后修改时间，每次添加或修改，都会自动更新，无法程序中手动为字段赋值
    is_delete = models.BooleanField(default=False, verbose_name="是否删除")

    class Meta:
        # 为抽象模型类, 用于其他模型来继承，数据库迁移时不会创建ModelBase表
        abstract = True

'''
这里有几点要特别说明：
抽象基类中有的元数据，子模型没有的话，直接继承；
抽象基类中有的元数据，子模型也有的话，直接覆盖；
子模型可以额外添加元数据；
抽象基类中的abstract=True这个元数据不会被继承。也就是说如果想让一个抽象基类的子模型，同样成为一个抽象基类，那你必须显式的在该子模型的Meta中同样声明一个abstract = True；
有一些元数据对抽象基类无效，比如db_table，首先是抽象基类本身不会创建数据表，其次它的所有子类也不会按照这个元数据来设置表名。
'''