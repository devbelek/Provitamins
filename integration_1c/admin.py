from django.contrib import admin
from django.utils.html import format_html
from .models import Product1C, SyncLog, ProductImage1C
from marketplace.models import Product
from django.contrib import messages
from marketplace.admin import ProductImageInline


class Product1CImageInline(admin.TabularInline):
    model = ProductImage1C
    extra = 0
    max_num = 3


class SyncLogInline(admin.TabularInline):
    model = SyncLog
    extra = 0
    readonly_fields = ('sync_type', 'status', 'message', 'created_at')
    can_delete = False
    max_num = 0

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Product1C)
class Product1CAdmin(admin.ModelAdmin):
    inlines = (SyncLogInline,)

    list_display = (
        'id', 'name_en', 'name', 'brand', 'manufacturer_country',
        'form', 'price', 'sale_price', 'status', 'published_product'
    )
    list_display_links = ('id', 'name', 'name_en')
    list_editable = ('price', 'sale_price', 'status', 'published_product')

    list_filter = [
        ('published_product', admin.BooleanFieldListFilter),
        ('brand', admin.RelatedFieldListFilter),
        ('manufacturer_country', admin.RelatedFieldListFilter),
        ('form', admin.RelatedFieldListFilter),
        ('categories', admin.RelatedFieldListFilter),
        ('status', admin.ChoicesFieldListFilter),
        ('is_hit', admin.BooleanFieldListFilter),
        ('is_sale', admin.BooleanFieldListFilter),
        ('is_recommend', admin.BooleanFieldListFilter),
        ('created_at', admin.DateFieldListFilter),
    ]

    search_fields = (
        'name', 'name_en', 'description',
        'flavor', 'dosage', 'vendor_code',
        'brand__name', 'manufacturer_country__name'
    )

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'categories',
                ('brand', 'manufacturer_country'),
                'form',
                ('name_en', 'name'),
                ('flavor', 'dosage'),
                'description',
                ('price', 'sale_price'),
                'status',
                'quantity',
                'vendor_code'
            )
        }),
        ('Дополнительные настройки', {
            'fields': (
                'similar_products',
                ('is_hit', 'is_sale', 'is_recommend'),
                'rating',
            ),
            'classes': ('collapse',)
        }),
        ('СЕО и публикация', {
            'fields': (
                'seo_keywords',
                'published_product',
            ),
            'classes': ('collapse',)
        }),
    )

    filter_horizontal = ('categories', 'similar_products')
    save_on_top = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'brand', 'manufacturer_country', 'form'
        ).prefetch_related('categories', 'similar_products')

    def published_status(self, obj):
        # Проверяем существование товара в основном каталоге
        if Product.objects.filter(vendor_code=obj.vendor_code).exists():
            return format_html(
                '<span style="color: green;">✔ Опубликован</span>'
            )
        return format_html(
            '<span style="color: red;">✖ Не опубликован</span>'
        )

    published_status.short_description = 'Статус публикации'

    actions = ['publish_products', 'unpublish_products']

    def publish_products(self, request, queryset):
        for product in queryset:
            if not product.is_published:
                # Проверяем наличие обязательных полей
                if not all([product.brand, product.manufacturer_country]):
                    self.message_user(
                        request,
                        f'Товар {product.name_en} не может быть опубликован. '
                        f'Заполните обязательные поля (Бренд, Страна производитель)',
                        level='ERROR'
                    )
                    continue

                # Проверяем описание
                if not product.description:
                    product.description = ""  # Устанавливаем пустую строку если нет описания

                try:
                    # Создаем новый товар в основном каталоге
                    new_product = Product.objects.create(
                        name=product.name or product.name_en,
                        vendor_code=product.vendor_code,
                        price=product.price,
                        status=product.status,
                        description=product.description,
                        brand=product.brand,
                        manufacturer_country=product.manufacturer_country,
                        form=product.form,
                        flavor=product.flavor,
                        dosage=product.dosage,
                        sale_price=product.sale_price,
                        is_hit=product.is_hit,
                        is_sale=product.is_sale,
                        is_recommend=product.is_recommend,
                        quantity=product.quantity or "1",
                        rating=product.rating,
                        seo_keywords=product.seo_keywords
                    )

                    # Добавляем категории если есть
                    if hasattr(product, 'categories'):
                        new_product.categories.set(product.categories.all())

                    # Логируем публикацию
                    SyncLog.objects.create(
                        product_1c=product,
                        sync_type='publish',
                        status=True,
                        message='Товар успешно опубликован в основном каталоге'
                    )

                    # Удаляем товар из 1С
                    product.delete()

                    self.message_user(
                        request,
                        f'Товар {product.name_en} успешно опубликован',
                        level='SUCCESS'
                    )

                except Exception as e:
                    self.message_user(
                        request,
                        f'Ошибка при публикации товара {product.name_en}: {str(e)}',
                        level='ERROR'
                    )

    publish_products.short_description = 'Опубликовать выбранные товары'

    def unpublish_products(self, request, queryset):
        for product in queryset:
            # Находим соответствующий товар в основном каталоге
            main_product = Product.objects.filter(vendor_code=product.vendor_code).first()
            if main_product:
                main_product.delete()

                # Логируем снятие с публикации
                SyncLog.objects.create(
                    product_1c=product,
                    sync_type='unpublish',
                    status=True,
                    message='Товар удален из основного каталога'
                )

    unpublish_products.short_description = 'Снять с публикации'

    def save_model(self, request, obj, form, change):
        if obj.is_published:
            # Проверяем обязательные поля перед публикацией
            if not all([obj.brand, obj.manufacturer_country]):
                messages.error(
                    request,
                    'Невозможно опубликовать товар. Заполните обязательные поля (Бренд, Страна производитель)'
                )
                obj.is_published = False
                super().save_model(request, obj, form, change)
                return

            # Если все проверки пройдены, публикуем товар
            self.publish_products(request, Product1C.objects.filter(pk=obj.pk))
        else:
            super().save_model(request, obj, form, change)


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ('product_1c', 'sync_type', 'status', 'created_at')
    list_filter = ('sync_type', 'status', 'created_at')
    search_fields = ('product_1c__name_en', 'product_1c__vendor_code', 'message')
    readonly_fields = ('product_1c', 'sync_type', 'status', 'message', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False