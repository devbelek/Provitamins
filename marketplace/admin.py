from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django import forms
from mptt.admin import MPTTModelAdmin
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

from .models import Catalogue, Category, Brand, Country, Form, Product, ProductReview, Order, OrderItem, OrderModerator
from .models import ProductImage, TelegramUsername


@admin.register(Catalogue)
class CatalogueAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['parent'] and cleaned_data['catalogue']:
            raise forms.ValidationError('Категория не может иметь родителя и каталог одновременно. Выберите одно из двух.')
        return cleaned_data


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    form = CategoryForm
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['parent'].queryset = Category.objects.filter(level=0)
        return super(CategoryAdmin, self).render_change_form(request, context, *args, **kwargs)


@admin.register(Brand)
class BrandAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')


@admin.register(Country)
class CountryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')


@admin.register(Form)
class FormAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    max_num = 3


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, DynamicArrayMixin):
    inlines = (ProductImageInline,)

    list_display = ('id', 'name', 'brand', 'manufacturer_country', 'form', 'price')
    list_display_links = ('id', 'name')
    list_filter = ('categories', 'brand', 'manufacturer_country', 'form', 'is_hit', 'is_sale', 'status', 'rating')
    search_fields = ('name', 'description')

    fieldsets = (
        (None, {
            'fields': (
                'categories', 'brand', 'manufacturer_country', 'form', 'name', 'description', 'price', 'sale_price',
                'status', 'rating', 'is_hit', 'is_sale', 'is_recommend', 'quantity', 'vendor_code',
        )}),
        ('СЕО ключевые слова', {
            'fields': ('seo_keywords',)
        })
    )

    def get_queryset(self, request):
        queryset = super(ProductAdmin, self).get_queryset(request)
        queryset = queryset.select_related('brand', 'manufacturer_country', 'form') \
                           .prefetch_related('categories')
        return queryset


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'full_name', 'rating', 'date_created', 'is_allow')
    list_display_links = ('id', 'product', 'full_name', 'rating', 'date_created', 'is_allow')
    list_filter = ('rating', 'is_allow', 'date_created')
    search_fields = ('product__name ', 'full_name', 'review')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_price', 'product_sale_price')

    def product_price(self, instance):
        return instance.product.price
    product_price.short_description = 'Цена товара'

    def product_sale_price(self, instance):
        return instance.product.sale_price or 'Нет акции'
    product_sale_price.short_description = 'Цена по акции'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderItemInline,)
    list_display = ('id', 'full_name', 'phone', 'status', 'date_created')
    list_display_links = ('id', 'full_name', 'phone', 'date_created', 'status')
    list_filter = ('status', 'date_created')
    search_fields = ('full_name', 'phone', 'email')


class OrderModeratorForm(forms.ModelForm):
    class Meta:
        model = OrderModerator
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        print('cleaned', cleaned_data)
        username = cleaned_data.get('telegram_nick')
        telegram_user = TelegramUsername.objects.filter(username=username).first()
        if not telegram_user:
            raise forms.ValidationError('Не удалось получить telegram_id')
        self.cleaned_data['telegram_id'] = telegram_user.telegram_id
        print('cleaned 2', cleaned_data)
        return cleaned_data

    def save(self, commit=True):
        moderator = super().save(commit=False)
        telegram_user = TelegramUsername.objects. filter(username=moderator.telegram_nick).first()
        moderator.telegram_id = telegram_user.telegram_id
        if commit:
            moderator.save()
        return moderator


@admin.register(OrderModerator)
class OrderModeratorAdmin(admin.ModelAdmin):
    form = OrderModeratorForm
    list_display = ('id', 'telegram_nick')
    list_display_links = ('id', 'telegram_nick')
    exclude = ('telegram_id',)
