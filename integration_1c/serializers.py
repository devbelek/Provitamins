from rest_framework import serializers
from .models import Product1C, SyncLog
from marketplace.models import Product


class Product1CSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product1C
        fields = ('name_en', 'vendor_code', 'price', 'status')

    def create(self, validated_data):
        vendor_code = validated_data.get('vendor_code')
        name_en = validated_data.get('name_en', '')
        price = validated_data.get('price')
        status = validated_data.get('status')

        # Проверяем существование товара в основном каталоге
        main_product = Product.objects.filter(vendor_code=vendor_code).first()

        if main_product:
            try:
                # Если товар существует в основном каталоге, обновляем его
                if name_en:
                    main_product.name_en = name_en
                if price:
                    main_product.price = price
                if status:
                    main_product.status = status
                main_product.save()

                # Создаем запись в 1С для логирования
                instance = Product1C.objects.create(
                    name_en=name_en,
                    vendor_code=vendor_code,
                    price=price,
                    status=status
                )

                # Логируем обновление
                SyncLog.objects.create(
                    product_1c=instance,
                    sync_type='update',
                    status=True,
                    message=(
                        f'Товар обновлен в основном каталоге. '
                        f'Артикул: {vendor_code}. '
                        f'Старая цена: {main_product.price}, новая цена: {price}'
                    )
                )

                # Удаляем запись из 1С после логирования
                instance.delete()

                return {
                    'name_en': name_en,
                    'vendor_code': vendor_code,
                    'price': price,
                    'status': status
                }
            except Exception as e:
                # Если произошла ошибка при обновлении
                SyncLog.objects.create(
                    product_1c=instance,
                    sync_type='update',
                    status=False,
                    message=f'Ошибка при обновлении товара: {str(e)}'
                )
                raise serializers.ValidationError(f"Ошибка при обновлении товара: {str(e)}")

        # Если товара нет в основном каталоге
        instance = Product1C.objects.filter(vendor_code=vendor_code).first()

        if instance:
            # Обновляем существующий товар в 1C
            old_price = instance.price

            if name_en:
                instance.name_en = name_en
            if price:
                instance.price = price
            if status:
                instance.status = status

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
            try:
                instance = Product1C.objects.create(
                    name_en=name_en,
                    vendor_code=vendor_code,
                    price=price,
                    status=status
                )

                # Логируем создание
                SyncLog.objects.create(
                    product_1c=instance,
                    sync_type='create',
                    status=True,
                    message='Товар успешно создан в 1C'
                )
            except Exception as e:
                raise serializers.ValidationError(f"Ошибка при создании товара: {str(e)}")

        return instance