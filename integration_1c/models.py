from django.db import models
from marketplace.models import Product

from marketplace.models import Country, Brand, Form


class Product1C(models.Model):
    STATUS_CHOICES = [
        ('in_stock', 'В наличии'),
        ('out_of_stock', 'Нет в наличии')
    ]

    name_en = models.CharField(
        max_length=255,
        verbose_name='Наименование (EN)',
        editable=False  # Неизменяемое поле
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Наименование на русском',
        blank=True,
        null=True
    )
    vendor_code = models.CharField(
        max_length=255,
        verbose_name='Артикул'
    )
    price = models.IntegerField(
        verbose_name='Цена'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='out_of_stock',
        verbose_name='Статус'
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Опубликовать товар'
    )

    # Остальные поля из Product для заполнения перед публикацией
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    manufacturer_country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    form = models.ForeignKey(Form, on_delete=models.SET_NULL, null=True, blank=True)
    description = RichTextField(blank=True, null=True)
    categories = models.ManyToManyField(Category, blank=True)
    flavor = models.CharField(max_length=255, blank=True, null=True)
    dosage = models.CharField(max_length=255, blank=True, null=True)
    sale_price = models.IntegerField(blank=True, null=True)
    is_hit = models.BooleanField(default=False)
    is_sale = models.BooleanField(default=False)
    is_recommend = models.BooleanField(default=False)
    quantity = models.CharField(max_length=255, blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    seo_keywords = ArrayField(models.CharField(max_length=255), blank=True, null=True)

    published_product = models.OneToOneField(
        'marketplace.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Опубликованный товар'
    )


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