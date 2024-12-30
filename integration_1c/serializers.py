from rest_framework import serializers
from .models import Product1C, SyncLog
from marketplace.models import Product


class Product1CSerializer(serializers.ModelSerializer):
    base_product_code = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Product1C
        fields = ('name_en', 'vendor_code', 'price', 'status', 'is_variation', 'base_product_code')

    def create(self, validated_data):
        vendor_code = validated_data['vendor_code']
        name_en = validated_data['name_en']
        price = validated_data['price']
        status = validated_data['status']
        is_variation = validated_data.get('is_variation', False)
        base_product_code = validated_data.pop('base_product_code', None)

        # Проверяем существование товара в основном каталоге
        main_product = Product.objects.filter(vendor_code=vendor_code).first()

        if main_product:
            try:
                # Обновляем существующий товар в основном каталоге
                main_product.name_en = name_en
                main_product.price = price
                main_product.status = status

                if is_variation and base_product_code:
                    base_product = Product.objects.filter(vendor_code=base_product_code).first()
                    main_product.base_product = base_product
                    main_product.is_variation = True

                main_product.save()

                # Создаем временную запись в 1С для логирования
                instance = Product1C.objects.create(
                    name_en=name_en,
                    vendor_code=vendor_code,
                    price=price,
                    status=status,
                    is_variation=is_variation
                )

                if is_variation and base_product_code:
                    base_product_1c = Product1C.objects.filter(vendor_code=base_product_code).first()
                    if base_product_1c:
                        instance.base_product = base_product_1c
                        instance.save()

                # Логируем обновление
                SyncLog.objects.create(
                    product_1c=instance,
                    sync_type='update',
                    status=True,
                    message=(
                        f'Товар обновлен в основном каталоге. '
                        f'Артикул: {vendor_code}, Name_EN: {name_en}. '
                        f'Старая цена: {main_product.price}, новая цена: {price}'
                    )
                )

                instance.delete()
                return validated_data

            except Exception as e:
                raise serializers.ValidationError(f"Ошибка при обновлении товара: {str(e)}")

        # Если товара нет в основном каталоге
        instance = Product1C.objects.filter(vendor_code=vendor_code).first()

        if instance:
            # Обновляем существующий товар в 1C
            old_data = {
                'name_en': instance.name_en,
                'price': instance.price
            }

            instance.name_en = name_en
            instance.price = price
            instance.status = status
            instance.is_variation = is_variation

            if is_variation and base_product_code:
                base_product_1c = Product1C.objects.filter(vendor_code=base_product_code).first()
                if base_product_1c:
                    instance.base_product = base_product_1c

            instance.save()

            SyncLog.objects.create(
                product_1c=instance,
                sync_type='update',
                status=True,
                message=(
                    f'Товар обновлен в 1C. '
                    f'Name_EN: {old_data["name_en"]} -> {name_en}, '
                    f'Цена: {old_data["price"]} -> {price}'
                )
            )
        else:
            try:
                base_product_1c = None
                if is_variation and base_product_code:
                    base_product_1c = Product1C.objects.filter(vendor_code=base_product_code).first()

                instance = Product1C.objects.create(
                    name_en=name_en,
                    vendor_code=vendor_code,
                    price=price,
                    status=status,
                    is_variation=is_variation,
                    base_product=base_product_1c
                )

                SyncLog.objects.create(
                    product_1c=instance,
                    sync_type='create',
                    status=True,
                    message=(
                        f'Товар создан в 1C. '
                        f'Артикул: {vendor_code}, Name_EN: {name_en}, '
                        f'Цена: {price}'
                    )
                )
            except Exception as e:
                raise serializers.ValidationError(f"Ошибка при создании товара: {str(e)}")

        return instance