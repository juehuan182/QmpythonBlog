from rest_framework import serializers

from shop.views import GoodsCategory
from shop.models import GoodsSPU, GoodsSKU


class GoodsCategorySerializer(serializers.Serializer):
    name = serializers.CharField(label='商品分类名称')
    category_type = serializers.IntegerField(label='商品分类级别')
    create_time = serializers.DateTimeField(label='创建时间')
    update_time = serializers.DateTimeField(label='更新时间')
    is_delete = serializers.BooleanField(label='是否删除')

    def create(self, validated_data):
        return GoodsCategory.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.category_type = validated_data.get('category_type', instance.category_type)
        instance.create_time = validated_data.get('create_time', instance.create_time)
        instance.update_time = validated_data.get('update_time', instance.update_time)
        instance.is_delete = validated_data.get('is_delete', instance.is_delete)

        instance.save()
        return instance



class GoodsSPUSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsSPU
        fields = '__all__'



class GoodsSKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsSKU
        fields = '__all__'

