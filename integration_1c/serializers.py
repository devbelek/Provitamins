from rest_framework import serializers
from .models import Product1C, SyncLog
from marketplace.models import Product


class Product1CSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product1C
        fields = ('name_en', 'vendor_code', 'price', 'status')

    def create(self, validated_data):
        vendor_code = validated_data['vendor_code']
        name_en = validated_data['name_en']
        price = validated_data['price']
        status = validated_data['status']

        # Проверяем существование товара в основном каталоге
        main_product = Product.objects.filter(vendor_code=vendor_code).first()

        if main_product:
            try:
                # Обновляем существующий товар в основном каталоге
                main_product.name_en = name_en
                main_product.price = price
                main_product.status = status
                main_product.save()

                # Создаем временную запись в 1С для логирования
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
                        f'Артикул: {vendor_code}, Name_EN: {name_en}. '
                        f'Старая цена: {main_product.price}, новая цена: {price}'
                    )
                )

                # Удаляем временную запись
                instance.delete()

                return validated_data

            except Exception as e:
                raise serializers.ValidationError(f"Ошибка при обновлении товара: {str(e)}")

        # Если товара нет в основном каталоге, проверяем наличие в 1C
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
            instance.save()

            # Логируем обновление
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
                # Создаем новый товар в 1C
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
                    message=(
                        f'Товар создан в 1C. '
                        f'Артикул: {vendor_code}, Name_EN: {name_en}, '
                        f'Цена: {price}'
                    )
                )
            except Exception as e:
                raise serializers.ValidationError(f"Ошибка при создании товара: {str(e)}")

        return instance