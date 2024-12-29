from rest_framework import serializers
from .models import Product1C, SyncLog
from marketplace.models import Product


class Product1CSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product1C
        fields = ('name_en', 'vendor_code', 'price', 'status')

    def create(self, validated_data):
        # Проверяем существование товара по артикулу
        instance = Product1C.objects.filter(
            vendor_code=validated_data['vendor_code']
        ).first()

        if instance:
            # Обновляем существующий товар
            old_price = instance.price  # Сохраняем старую цену для лога

            # Обновляем все поля из validated_data
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()

            # Обновляем опубликованный товар если есть
            if instance.published_product:
                product = instance.published_product
                product.name = validated_data.get('name_en', product.name)
                product.price = validated_data.get('price', product.price)
                product.status = validated_data.get('status', product.status)
                product.save()

            # Логируем обновление
            SyncLog.objects.create(
                product_1c=instance,
                sync_type='update',
                status=True,
                message=f'Товар обновлен из 1С. Старая цена: {old_price}, новая цена: {instance.price}. '
                        f'Артикул: {instance.vendor_code}'
            )

            return instance

        # Создаем новый товар если не существует
        instance = Product1C.objects.create(**validated_data)

        # Логируем создание
        SyncLog.objects.create(
            product_1c=instance,
            sync_type='create',
            status=True,
            message=f'Товар создан из 1С. Артикул: {instance.vendor_code}'
        )

        return instance

    def update(self, instance, validated_data):
        old_price = instance.price  # Сохраняем старую цену для лога

        # Обновляем все поля из validated_data
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        # Обновляем опубликованный товар если есть
        if instance.published_product:
            product = instance.published_product
            product.name = validated_data.get('name_en', product.name)
            product.price = validated_data.get('price', product.price)
            product.status = validated_data.get('status', product.status)
            product.save()

        # Логируем обновление
        SyncLog.objects.create(
            product_1c=instance,
            sync_type='update',
            status=True,
            message=f'Товар обновлен из 1С. Старая цена: {old_price}, новая цена: {instance.price}. '
                    f'Артикул: {instance.vendor_code}'
        )

        return instance