from rest_framework import serializers
from .models import Product1C, SyncLog
from marketplace.models import Product


class Product1CSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product1C
        fields = ('name_en', 'vendor_code', 'price', 'status')

    def create(self, validated_data):
        vendor_code = validated_data['vendor_code']

        # Сначала ищем товар в таблице Product1C
        instance = Product1C.objects.filter(vendor_code=vendor_code).first()

        if instance:
            old_price = instance.price

            # Обновляем товар в 1C
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()

            # Проверяем есть ли связанный опубликованный товар
            if instance.published_product:
                product = instance.published_product
            else:
                # Если нет связанного товара, ищем по артикулу в основной таблице
                product = Product.objects.filter(vendor_code=vendor_code).first()
                if product:
                    # Если нашли, связываем с товаром 1C
                    instance.published_product = product
                    instance.save()

            # Если есть связанный товар, обновляем его
            if product:
                product.name = validated_data.get('name_en', product.name)
                product.price = validated_data.get('price', product.price)
                product.status = validated_data.get('status', product.status)
                product.save()

            # Логируем обновление
            SyncLog.objects.create(
                product_1c=instance,
                sync_type='update',
                status=True,
                message=(
                    f'Товар обновлен. '
                    f'Старая цена: {old_price}, новая цена: {instance.price}. '
                    f'Артикул: {instance.vendor_code}. '
                    f'Основной товар: {"обновлен" if product else "не найден"}'
                )
            )

            return instance

        # Если товар не найден в 1C, создаем новый
        instance = Product1C.objects.create(**validated_data)

        # Проверяем существует ли товар в основной таблице
        product = Product.objects.filter(vendor_code=vendor_code).first()
        if product:
            # Если существует, связываем с товаром 1C
            instance.published_product = product
            instance.save()

            # И обновляем его данные
            product.name = validated_data.get('name_en', product.name)
            product.price = validated_data.get('price', product.price)
            product.status = validated_data.get('status', product.status)
            product.save()

        # Логируем создание
        SyncLog.objects.create(
            product_1c=instance,
            sync_type='create',
            status=True,
            message=(
                f'Товар создан в 1C. '
                f'Артикул: {instance.vendor_code}. '
                f'Основной товар: {"найден и обновлен" if product else "не найден"}'
            )
        )

        return instance