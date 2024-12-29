from django.contrib import admin
from django.utils.html import format_html
from .models import Product1C, SyncLog
from marketplace.models import Product


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
    list_display = (
        'id', 'name_en', 'name', 'vendor_code',
        'price', 'status', 'is_published',
        'published_status', 'created_at'
    )
    list_editable = ('name', 'price', 'status', 'is_published')
    list_filter = ('status', 'is_published', 'created_at')
    search_fields = ('name_en', 'name', 'vendor_code')
    readonly_fields = ('name_en', 'published_status', 'created_at')
    inlines = [SyncLogInline]

    fieldsets = (
        ('Информация из 1С (неизменяемая)', {
            'fields': ('name_en', 'created_at'),
            'classes': ('collapse',)
        }),
        ('Основная информация', {
            'fields': (
                'name', 'vendor_code', 'price', 'status',
                'categories', 'brand', 'manufacturer_country', 'form',
                'description', 'flavor', 'dosage'
            )
        }),
        ('Цены и статусы', {
            'fields': (
                'sale_price', 'is_hit', 'is_sale', 'is_recommend',
                'quantity', 'rating'
            )
        }),
        ('SEO', {
            'fields': ('seo_keywords',),
            'classes': ('collapse',)
        }),
        ('Публикация', {
            'fields': ('is_published', 'published_status')
        })
    )

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
                # Создаем новый товар в основном каталоге
                new_product = Product.objects.create(
                    name=product.name or product.name_en,
                    vendor_code=product.vendor_code,
                    price=product.price,
                    status=product.status,
                    description=product.description or "",
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
            # Если установлен флаг публикации, публикуем товар
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