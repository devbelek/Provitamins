from rest_framework import serializers
from .models import Product1C, SyncLog
from marketplace.models import Product


class Product1CSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product1C
        fields = ('name_en', 'vendor_code', 'price', 'status')

    def create(self, validated_data):
        vendor_code = validated_data['vendor_code']

        # Проверяем существование товара в основном каталоге
        main_product = Product.objects.filter(vendor_code=vendor_code).first()

        if main_product:
            # Если товар существует в основном каталоге, обновляем его
            main_product.name_en = validated_data['name_en']
            main_product.price = validated_data['price']
            main_product.status = validated_data['status']
            main_product.save()

            # Создаем запись в 1С для логирования
            instance = Product1C.objects.create(
                name_en=validated_data['name_en'],
                vendor_code=validated_data['vendor_code'],
                price=validated_data['price'],
                status=validated_data['status']
            )

            # Логируем обновление
            SyncLog.objects.create(
                product_1c=instance,
                sync_type='update',
                status=True,
                message=f'Товар обновлен в основном каталоге. Артикул: {vendor_code}'
            )

            # Удаляем запись из 1С после логирования
            instance.delete()

            return validated_data

        # Если товара нет в основном каталоге
        instance = Product1C.objects.filter(vendor_code=vendor_code).first()

        if instance:
            # Обновляем существующий товар в 1C
            old_price = instance.price
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()

            # Логируем обновление
            SyncLog.objects.create(
                product_1c=instance,
                sync_type='update',
                status=True,
                message=f'Товар обновлен в 1C. Старая цена: {old_price}, новая цена: {instance.price}'
            )
        else:
            # Создаем новый товар в 1C
            instance = Product1C.objects.create(**validated_data)

            # Логируем создание
            SyncLog.objects.create(
                product_1c=instance,
                sync_type='create',
                status=True,
                message='Товар создан в 1C'
            )

        return instance