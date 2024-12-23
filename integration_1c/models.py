from django.db import models
from marketplace.models import Product

from marketplace.models import Country, Brand, Form


class Product1C(models.Model):
    """Модель для товаров, поступающих из 1С"""
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Бренд'
    )
    manufacturer_country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Страна производитель'
    )
    form = models.ForeignKey(
        Form,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Форма'
    )
    name_en = models.CharField(
        max_length=255,
        verbose_name='Наименование (EN)',
        editable=False
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Наименование на русском',
        blank=True
    )
    vendor_code = models.CharField(
        max_length=255,
        verbose_name='Артикул',
        unique=True
    )
    price = models.IntegerField(verbose_name='Цена')
    status = models.CharField(
        max_length=20,
        choices=Product.ProductStatus.choices,
        default=Product.ProductStatus.out_of_stock,
        verbose_name='Статус'
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
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
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