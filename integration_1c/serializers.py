from rest_framework import serializers
from .models import Product1C, SyncLog
from marketplace.models import Product


class Product1CSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product1C
        fields = ('name_en', 'vendor_code', 'price', 'status')

    def validate_vendor_code(self, value):
        """
        Проверяем существование товара с таким артикулом
        """
        instance = self.instance  # Текущий объект, если это обновление
        # Проверяем существует ли товар с таким артикулом
        if Product1C.objects.filter(vendor_code=value).exists():
            raise serializers.ValidationError("Товар из 1С с таким Артикул уже существует.")
        return value

    def create(self, validated_data):
        # Проверяем существование товара
        instance = Product1C.objects.filter(
            vendor_code=validated_data['vendor_code']
        ).first()

        if instance:
            # Обновляем существующий товар
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()

            # Обновляем опубликованный товар если есть
            if instance.published_product:
                product = instance.published_product
                product.price = validated_data.get('price', product.price)
                product.status = validated_data.get('status', product.status)
                product.save()

            # Логируем
            SyncLog.objects.create(
                product_1c=instance,
                sync_type='update',
                status=True,
                message=f'Товар обновлен из 1С. Старая цена: {instance.price}, новая цена: {validated_data["price"]}'
            )

            return instance

        # Создаем новый товар
        instance = super().create(validated_data)
        SyncLog.objects.create(
            product_1c=instance,
            sync_type='create',
            status=True,
            message='Товар создан из 1С'
        )

        return instance