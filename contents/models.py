from ckeditor.fields import RichTextField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Banner(models.Model):
    pass

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"

    def __str__(self):
        return "Баннер"


class BannerImage(models.Model):
    """Модель изображения баннера"""
    banner = models.ForeignKey(Banner, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField("Изображение", upload_to="banners/")

    #belek
    link = models.URLField("Ссылка", blank=True, null=True)

    class Meta:
        verbose_name = "Изображение баннера"
        verbose_name_plural = "Изображения баннеров"

    def __str__(self):
        return f"Изображение баннера №{self.id}"


class Ticker(models.Model):
    """Модель бегущей строки"""
    text = models.CharField("Текст", max_length=350)

    class Meta:
        verbose_name = "Бегущая строка"
        verbose_name_plural = "Бегущие строки"

    def __str__(self):
        return self.text


class FAQ(models.Model):
    """Модель FAQ"""
    question = models.CharField("Вопрос", max_length=350)
    answer = models.TextField("Ответ")
    sort = models.PositiveIntegerField("Сортировка", default=0)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"
        ordering = ["sort"]

    def __str__(self):
        return self.question


class Contact(models.Model):
    """Модель контактов"""
    phone = PhoneNumberField("Телефон", max_length=300, blank=True, null=True)
    phone2 = PhoneNumberField("Телефон 2", max_length=300, blank=True, null=True)
    email = models.EmailField("Email", blank=True, null=True)
    address = models.CharField("Адрес", max_length=300, blank=True, null=True)

    #belek
    address_extra = models.CharField("Дополнительный адрес", max_length=300, blank=True, null=True)

    work_time = models.CharField("Время работы", max_length=300, blank=True, null=True)
    instagram_image = models.ImageField("Изображение Instagram", upload_to="main_page/instagram/", blank=True,
                                        null=True)
    instagram_link = models.URLField("Ссылка на Instagram", blank=True, null=True)

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"

    def __str__(self):
        return "Контакты"


class ContactSocialMedia(models.Model):
    """Модель социальных сетей"""

    class SocialMediaType(models.TextChoices):
        TELEGRAM = "telegram", "Telegram"
        INSTAGRAM = "instagram", "Instagram"
        TIKTOK = "tiktok", "TikTok"
        WHATSAPP = "whatsapp", "WhatsApp"

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="socials")
    link = models.URLField("Ссылка")
    type = models.CharField("Тип", max_length=20, choices=SocialMediaType.choices, unique=True)
    icon = models.FileField("Иконка", upload_to="main_page/social_media/", blank=True, null=True)

    class Meta:
        verbose_name = "Социальная сеть"
        verbose_name_plural = "Социальные сети"


class Review(models.Model):
    """Модель отзывов"""
    full_name = models.CharField("ФИО", max_length=300, blank=True, null=True)
    icon = models.FileField("Иконка", upload_to="main_page/reviews/", blank=True, null=True)
    review = models.TextField("Текст")

    rating = models.IntegerField("Рейтинг", validators=[MinValueValidator(1), MaxValueValidator(5)], default=5)
    sort = models.PositiveIntegerField("Сортировка", default=0)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["sort"]

    def __str__(self):
        return self.full_name or f"Отзыв №{self.id}"


class InfoBlock(models.Model):
    """Модель информационного блока"""
    description = RichTextField("Описание")
    image = models.ImageField("Иконка", upload_to="main_page/info_blocks/")

    class Meta:
        verbose_name = "Информационный блок"
        verbose_name_plural = "Информационный блок"

    def __str__(self):
        return "Информационный блок"


class BlogPost(models.Model):
    """Модель поста блога"""
    title = models.CharField("Заголовок", max_length=300)
    image = models.ImageField("Изображение", upload_to="main_page/blog_posts/")
    description = RichTextField("Описание")

    class Meta:
        verbose_name = "Пост блога"
        verbose_name_plural = "Посты блога"

    def __str__(self):
        return self.title


class Requisite(models.Model):
    """Реквизиты"""
    bank_name = models.CharField(
        max_length=255,
        verbose_name="Название банка"
    )
    text = models.CharField(
        max_length=255,
        verbose_name="Содержание"
    )
    owner_name = models.CharField(
        max_length=255,
        verbose_name="Реквизиты получателя"
    )

    class Meta:
        verbose_name = "Реквизит"
        verbose_name_plural = "Реквизиты"

    def __str__(self):
        return self.text


class Delivery(models.Model):
    """Модель доставки"""
    title = models.CharField("Заголовок", max_length=300)
    description = RichTextField("Описание")
    icon = models.FileField("Иконка", upload_to="main_page/deliveries/")

    class Meta:
        verbose_name = "Доставка"
        verbose_name_plural = "Доставки"

    def __str__(self):
        return self.title


class DenialOfResponsibility(models.Model):
    """Модель отказа от ответственности"""
    text = RichTextField("Текст")

    class Meta:
        verbose_name = "Отказ от ответственности"
        verbose_name_plural = "Отказ от ответственности"

    def __str__(self):
        return 'Отказ от ответственности'
