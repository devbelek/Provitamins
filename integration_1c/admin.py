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
                'name', 'vendor_code',
                'price', 'status'
            )
        }),
        ('Публикация', {
            'fields': (
                'is_published',
                'published_status',
                'published_product'
            )
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.published_product:
            return self.readonly_fields + ('vendor_code',)
        return self.readonly_fields

    def published_status(self, obj):
        if obj.published_product:
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
                product.is_published = True
                product.save()

                if product.published_product:
                    # Обновляем существующий товар
                    prod = product.published_product
                else:
                    # Создаем новый товар
                    prod = Product(
                        vendor_code=product.vendor_code,
                        name=product.name or product.name_en,
                        price=product.price,
                        status=product.status
                    )

                # Обновляем данные
                prod.name = product.name or product.name_en
                prod.price = product.price
                prod.status = product.status
                prod.save()

                product.published_product = prod
                product.save()

                # Логируем публикацию
                SyncLog.objects.create(
                    product_1c=product,
                    sync_type='publish',
                    status=True,
                    message='Товар успешно опубликован'
                )

    publish_products.short_description = 'Опубликовать выбранные товары'

    def unpublish_products(self, request, queryset):
        for product in queryset:
            if product.is_published:
                product.is_published = False
                product.save()

                if product.published_product:
                    product.published_product.delete()
                    product.published_product = None
                    product.save()

                # Логируем снятие с публикации
                SyncLog.objects.create(
                    product_1c=product,
                    sync_type='unpublish',
                    status=True,
                    message='Товар снят с публикации'
                )

    unpublish_products.short_description = 'Снять с публикации'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.is_published and not obj.published_product:
            # Автоматическая публикация при установке флага
            self.publish_products(request, Product1C.objects.filter(pk=obj.pk))


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