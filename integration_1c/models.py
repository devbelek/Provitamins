from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from marketplace.models import Product, Brand, Country, Form, Category
from django.utils.html import format_html
from ckeditor.fields import RichTextField
from django_better_admin_arrayfield.models.fields import ArrayField


class ProductImage1C(models.Model):
    """Модель изображения товара из 1С"""
    product = models.ForeignKey('Product1C', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images_1c', verbose_name='Изображение товара')

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'


class Product1C(models.Model):
    base_product = models.ForeignKey(
        'marketplace.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='product1c_variations',
        verbose_name='Базовый товар',
        help_text='Если это вариация, укажите базовый товар'
    )
    is_variation = models.BooleanField(
        default=False,
        verbose_name='Является вариацией',
        help_text='Отметьте, если это вариация другого товара',
        null=True,
        blank=True,
    )
    similar_products = models.ManyToManyField(
        'self',
        verbose_name="Похожие товары",
        symmetrical=True,
        blank=True,
        help_text="Товары с похожими характеристиками (например, тот же продукт с другим вкусом)"
    )

    categories = models.ManyToManyField(
        Category,
        verbose_name='Категории',
        related_name='products_1c',
        blank=True,
        )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Бренд',
        related_name='products_1c'
    )
    manufacturer_country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        verbose_name='Страна производитель',
        related_name='products_1c',
        null=True
    )
    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        verbose_name='Форма',
        related_name='products_1c',
        blank=True,
        null=True
    )

    flavor = models.CharField(max_length=255, verbose_name='Вкус', blank=True, null=True)
    dosage = models.CharField(max_length=255, verbose_name='Дозировка', blank=True, null=True)
    flavorArray = models.URLField(blank=True, null=True)
    dosageArray = models.URLField(blank=True, null=True)

    name_en = models.CharField(max_length=255, verbose_name='Наименование (EN)')
    name = models.CharField(max_length=255, verbose_name='Наименование товара', blank=True, null=True)
    description = RichTextField(verbose_name='Описание товара', blank=True, null=True)
    price = models.IntegerField(verbose_name='Цена', blank=True, null=True)
    sale_price = models.IntegerField(verbose_name='Цена со скидкой', blank=True, null=True)
    status = models.CharField(max_length=20, choices=Product.ProductStatus.choices,
                              default=Product.ProductStatus.in_stock,
                              verbose_name='Статус товара')
    is_hit = models.BooleanField(default=False, verbose_name='Хит')
    is_sale = models.BooleanField(default=False, verbose_name='Акция')
    is_recommend = models.BooleanField(default=False, verbose_name='Рекомендуемый')
    quantity = models.CharField(max_length=255, verbose_name='Количество в упаковке', blank=True, null=True)
    vendor_code = models.CharField(max_length=255, verbose_name='Артикул')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Рейтинг',
        blank=True,
        null=True
    )
    seo_keywords = ArrayField(models.CharField(max_length=255), verbose_name='Ключевые слова', blank=True, null=True)

    # Поля для 1С
    published_product = models.BooleanField(default=False, verbose_name='Модерацию')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f"{self.name_en} ({self.vendor_code})"

    class Meta:
        verbose_name = 'Товар 1с'
        verbose_name_plural = 'Товары 1с'


class SyncLog(models.Model):
    """Модель для логирования синхронизации"""
    SYNC_TYPES = (
        ('create', 'Создание'),
        ('update', 'Обновление'),
        ('publish', 'Публикация'),
    )

    product_1c = models.ForeignKey(
        Product1C,
        on_delete=models.CASCADE,
        verbose_name='Товар 1С'
    )
    sync_type = models.CharField(
        max_length=20,
        choices=SYNC_TYPES,
        verbose_name='Тип синхронизации'
    )
    status = models.BooleanField(
        default=True,
        verbose_name='Статус'
    )
    message = models.TextField(
        blank=True,
        verbose_name='Сообщение'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата'
    )

    class Meta:
        verbose_name = 'Лог синхронизации'
        verbose_name_plural = 'Логи синхронизации'
        ordering = ['-created_at']