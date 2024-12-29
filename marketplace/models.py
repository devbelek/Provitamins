from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django_better_admin_arrayfield.models.fields import ArrayField
from mptt.models import MPTTModel
from ckeditor.fields import RichTextField
from phonenumber_field.modelfields import PhoneNumberField


class Catalogue(models.Model):
    """Модель каталога товаров"""
    name = models.CharField(max_length=255, verbose_name='Название каталога')
    icon = models.FileField(upload_to='catalogue_icons', verbose_name='Иконка каталога')
    sort = models.PositiveIntegerField("Сортировка", default=0)

    class Meta:
        verbose_name = 'Каталог'
        verbose_name_plural = 'Каталоги'
        ordering = ['sort']

    def __str__(self):
        return self.name


class Category(MPTTModel):
    """Модель категории товара"""
    catalogue = models.ForeignKey(Catalogue, on_delete=models.CASCADE, verbose_name='Каталог',
                                  related_name='categories', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
                               verbose_name='Родительская категория')

    name = models.CharField(max_length=255, verbose_name='Название категории')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        if self.level == 0:
            return f"{self.name} <-- {self.catalogue.name if self.catalogue else 'Без каталога'}"
        return (f"{self.name} <-- {self.parent.name if self.parent else 'Без родительской категории'} "
                f"<-- {self.parent.catalogue.name if self.parent.catalogue else 'Без каталога'}")


class Brand(models.Model):
    """Модель бренда товара"""
    name = models.CharField(max_length=255, verbose_name='Наименование бренда')
    sort = models.PositiveIntegerField("Сортировка", default=0)

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'
        ordering = ['sort']

    def __str__(self):
        return self.name


class Country(models.Model):
    """Модель страны"""
    name = models.CharField(max_length=255, verbose_name='Наименование страны')
    sort = models.PositiveIntegerField("Сортировка", default=0)

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'
        ordering = ['sort']

    def __str__(self):
        return self.name


class Form(models.Model):
    """Модель формы товара"""
    name = models.CharField(max_length=255, verbose_name='Наименование формы')
    sort = models.PositiveIntegerField("Сортировка", default=0)

    class Meta:
        verbose_name = 'Форма'
        verbose_name_plural = 'Формы'
        ordering = ['sort']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Модель товара"""

    class ProductStatus(models.TextChoices):
        in_stock = 'in_stock', 'В наличии'
        out_of_stock = 'out_of_stock', 'Нет в наличии'

    base_product = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='variations',
        verbose_name='Базовый товар',
        help_text='Если это вариация, укажите базовый товар'
    )
    is_variation = models.BooleanField(
        default=False,
        verbose_name='Является вариацией',
        help_text='Отметьте, если это вариация другого товара'
    )

    categories = models.ManyToManyField(Category, verbose_name='Категории', related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name='Бренд', related_name='products')
    manufacturer_country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name='Страна производитель',
                                             related_name='products')
    form = models.ForeignKey(Form, on_delete=models.CASCADE, verbose_name='Форма', related_name='products', blank=True,
                             null=True)

    similar_products = models.ManyToManyField(
        'self',
        verbose_name="Похожие товары",
        symmetrical=True,
        blank=True,
        help_text="Товары с похожими характеристиками (например, тот же продукт с другим вкусом)"
    )

    flavor = models.CharField(max_length=255, verbose_name='Вкус', blank=True, null=True)
    dosage = models.CharField(max_length=255, verbose_name='Дозировка', blank=True, null=True)
    flavorArray = models.URLField(blank=True, null=True)
    dosageArray = models.URLField(blank=True, null=True)

    name_en = models.CharField(max_length=255, verbose_name='Наименование (EN)', blank=True, null=True)
    name = models.CharField(max_length=255, verbose_name='Наименование товара')
    description = RichTextField(verbose_name='Описание товара')
    price = models.IntegerField(verbose_name='Цена')
    sale_price = models.IntegerField(verbose_name='Цена со скидкой', blank=True, null=True)
    status = models.CharField(max_length=20, choices=ProductStatus.choices, default=ProductStatus.in_stock,
                              verbose_name='Статус товара')
    is_hit = models.BooleanField(default=False, verbose_name='Хит')
    is_sale = models.BooleanField(default=False, verbose_name='Акция')
    is_recommend = models.BooleanField(default=False, verbose_name='Рекомендуемый')
    quantity = models.CharField(max_length=255, verbose_name='Количество в упаковке')
    quantityArray = models.URLField(blank=True, null=True)
    vendor_code = models.CharField(max_length=255, verbose_name='Артикул')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Рейтинг',
        blank=True,
        null=True
    )
    seo_keywords = ArrayField(models.CharField(max_length=255), verbose_name='Ключевые слова', blank=True, null=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    @property
    def current_price(self):
        return self.sale_price if self.sale_price else self.price

    @property
    def first_category(self):
        return self.categories.all().first()

    def get_all_variations(self):
        """Получить все вариации для этого товара"""
        if self.is_variation:
            # Если это вариация, получаем от базового товара
            return self.base_product.variations.all()
        # Если это базовый товар, получаем его вариации
        return self.variations.all()

    def get_variations_by_type(self, variation_type):
        """Получить вариации определенного типа"""
        variations = self.get_all_variations()
        return variations.filter(variation_type=variation_type)


class ProductImage(models.Model):
    """Модель изображения товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images', verbose_name='Изображение товара')

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'

    def __str__(self):
        return self.product.name


class ProductReview(models.Model):
    """Отзыв на товар"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    review = models.TextField(verbose_name='Отзыв')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Рейтинг'
    )
    is_allow = models.BooleanField(default=False, verbose_name='Опубликовать')

    class Meta:
        verbose_name = 'Отзыв на товар'
        verbose_name_plural = 'Отзывы на товары'

    def __str__(self):
        return self.product.name


class Order(models.Model):
    """Модель заказа"""

    class OrderStatus(models.TextChoices):
        new = 'new', 'Новый'
        in_progress = 'in_progress', 'В обработке'
        completed = 'completed', 'Завершен'

    date_created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.new,
                              verbose_name='Статус заказа')
    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    phone = models.CharField(max_length=255, verbose_name='Телефон')
    total_price = models.IntegerField(verbose_name='Общая стоимость заказа', blank=True, null=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ №{self.id}'


class OrderItem(models.Model):
    """Модель товара в заказе"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(verbose_name='Количество товара')

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    def __str__(self):
        return f'{self.product.name} в заказе №{self.order.id}'


class OrderModerator(models.Model):
    """Модель модератора заказов"""
    telegram_nick = models.CharField(max_length=255, verbose_name='Ник в телеграме', unique=True)
    telegram_id = models.CharField(max_length=255, verbose_name='ID в телеграме')

    class Meta:
        verbose_name = 'Модератор заказов'
        verbose_name_plural = 'Модераторы заказов'

    def __str__(self):
        return self.telegram_nick


class TelegramUsername(models.Model):
    """Модель telegram username"""
    username = models.CharField(max_length=255, verbose_name='Username')
    telegram_id = models.CharField(max_length=255, verbose_name='ID в телеграме', unique=True)

    class Meta:
        verbose_name = 'Telegram username'
        verbose_name_plural = 'Telegram usernames'

    def __str__(self):
        return self.username
