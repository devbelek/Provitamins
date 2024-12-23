from rest_framework import serializers
from .models import Product1C, SyncLog


class Product1CSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product1C
        fields = ('name_en', 'vendor_code', 'price', 'status')

    def create(self, validated_data):
        instance = Product1C.objects.filter(
            vendor_code=validated_data['vendor_code']
        ).first()

        if instance:
            # Обновляем существующий товар в Product1C
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()

            # Если товар уже опубликован, обновляем его в основной таблице
            if instance.published_product:
                product = instance.published_product
                product.price = validated_data.get('price', product.price)
                product.status = validated_data.get('status', product.status)
                product.save()

            # Логируем обновление
            SyncLog.objects.create(
                product_1c=instance,
                sync_type='update',
                message='Товар обновлен из 1С'
            )
        else:
            # Ищем товар в основной таблице по артикулу
            existing_product = Product.objects.filter(
                vendor_code=validated_data['vendor_code']
            ).first()

            # Создаем запись в Product1C
            instance = super().create(validated_data)

            if existing_product:
                # Если товар существует в основной таблице, связываем их
                instance.published_product = existing_product
                instance.is_published = True
                instance.save()

                # Обновляем основной товар
                existing_product.price = validated_data.get('price', existing_product.price)
                existing_product.status = validated_data.get('status', existing_product.status)
                existing_product.save()

            # Логируем создание
            SyncLog.objects.create(
                product_1c=instance,
                sync_type='create',
                message='Товар создан из 1С'
            )

        return instance