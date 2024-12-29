from django.db import models
from marketplace.models import Product, Brand, Country, Form, Category
from django.utils.html import format_html
from ckeditor.fields import RichTextField
from django_better_admin_arrayfield.models.fields import ArrayField


class Product1C(models.Model):
    """Модель для товаров, поступающих из 1С"""
    name_en = models.CharField(
        max_length=255,
        verbose_name='Наименование (EN)',
        editable=False
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Наименование на русском',
        blank=True,
        null=True
    )
    vendor_code = models.CharField(
        max_length=255,
        verbose_name='Артикул',
        unique=True
    )
    price = models.IntegerField(
        verbose_name='Цена'
    )
    status = models.CharField(
        max_length=20,
        choices=Product.ProductStatus.choices,
        default=Product.ProductStatus.out_of_stock,
        verbose_name='Статус товара'
    )

    # Поля из основной модели Product
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Бренд'
    )
    manufacturer_country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Страна производитель'
    )
    form = models.ForeignKey(
        Form,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Форма'
    )
    description = RichTextField(
        verbose_name='Описание товара',
        blank=True,
        null=True
    )
    categories = models.ManyToManyField(
        'marketplace.Category',  # Исправляем ссылку на модель Category
        verbose_name='Категории',
        blank=True
    )
    flavor = models.CharField(
        max_length=255,
        verbose_name='Вкус',
        blank=True,
        null=True
    )
    dosage = models.CharField(
        max_length=255,
        verbose_name='Дозировка',
        blank=True,
        null=True
    )
    sale_price = models.IntegerField(
        verbose_name='Цена со скидкой',
        blank=True,
        null=True
    )
    is_hit = models.BooleanField(
        default=False,
        verbose_name='Хит'
    )
    is_sale = models.BooleanField(
        default=False,
        verbose_name='Акция'
    )
    is_recommend = models.BooleanField(
        default=False,
        verbose_name='Рекомендуемый'
    )
    quantity = models.CharField(
        max_length=255,
        verbose_name='Количество в упаковке',
        blank=True,
        null=True
    )
    rating = models.IntegerField(
        verbose_name='Рейтинг',
        blank=True,
        null=True
    )
    seo_keywords = ArrayField(
        models.CharField(max_length=255),
        verbose_name='Ключевые слова',
        blank=True,
        null=True
    )

    is_published = models.BooleanField(
        default=False,
        verbose_name='Опубликовать товар'
    )
    published_product = models.OneToOneField(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Опубликованный товар'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Товар из 1С'
        verbose_name_plural = 'Товары из 1С'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name_en} ({self.vendor_code})"


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