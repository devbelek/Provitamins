from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from .models import Banner, BannerImage, Ticker, FAQ, Contact, ContactSocialMedia, Review
from .models import InfoBlock, BlogPost, Requisite, Delivery, DenialOfResponsibility


class BannerImageInline(admin.TabularInline):
    model = BannerImage
    extra = 1
    max_num = 5
    fields = ('image', 'link')


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    inlines = (BannerImageInline,)

    list_display = ('id', '__str__')
    list_display_links = ('id', '__str__')

    readonly_fields = ('custom_description',)

    def custom_description(self, obj):
        return "Баннер может иметь не более 5 изображений"

    custom_description.short_description = 'Примечание'

    def has_add_permission(self, request):
        has_permission = super().has_add_permission(request)
        if has_permission and Banner.objects.exists():
            has_permission = False
        return has_permission


@admin.register(Ticker)
class TickerAdmin(admin.ModelAdmin):
    list_display = ('id', 'text')
    list_display_links = ('id', 'text')


@admin.register(FAQ)
class FAQAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'question')
    list_display_links = ('id', 'question')
    exclude = ('sort', )


class ContactSocialMediaInline(admin.StackedInline):
    model = ContactSocialMedia
    extra = 1


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    inlines = (ContactSocialMediaInline,)

    list_display = ('id', 'phone', 'phone2', 'email', 'address', 'work_time')
    list_display_links = ('id', 'phone', 'phone2', 'email', 'address', 'work_time')

    def has_add_permission(self, request):
        has_permission = super().has_add_permission(request)
        if has_permission and Contact.objects.exists():
            has_permission = False
        return has_permission


@admin.register(Review)
class ReviewAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'full_name', 'rating')
    list_display_links = ('id', 'full_name', 'rating')
    search_fields = ('full_name', 'review')
    exclude = ('sort', )


@admin.register(InfoBlock)
class InfoBlockAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'short_description')
    list_display_links = ('id', '__str__', 'short_description')
    search_fields = ('description', )

    def has_add_permission(self, request):
        has_permission = super().has_add_permission(request)
        if has_permission and InfoBlock.objects.exists():
            has_permission = False
        return has_permission

    def short_description(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description

    short_description.short_description = 'Описание'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'description')


@admin.register(Requisite)
class RequisiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'text')
    list_display_links = ('id', 'text')


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')


@admin.register(DenialOfResponsibility)
class DenialOfResponsibilityAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__')
    list_display_links = ('id', '__str__')

    def has_add_permission(self, request):
        has_permission = super().has_add_permission(request)
        if has_permission and DenialOfResponsibility.objects.exists():
            has_permission = False
        return has_permission
