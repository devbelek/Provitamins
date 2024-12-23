from rest_framework import serializers

from .models import Banner, FAQ, Ticker, Contact, ContactSocialMedia, Review, InfoBlock, BlogPost, Requisite
from .models import Delivery, BannerImage, DenialOfResponsibility


class BannerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerImage
        fields = ('image', 'link')


class BannerSerializer(serializers.ModelSerializer):
    images = BannerImageSerializer(many=True)

    class Meta:
        model = Banner
        fields = '__all__'


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'


class TickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticker
        fields = '__all__'


class ContactSocialMediaSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=ContactSocialMedia.SocialMediaType.choices)

    class Meta:
        model = ContactSocialMedia
        exclude = ('contact',)


class ContactSerializer(serializers.ModelSerializer):
    socials = ContactSocialMediaSerializer(many=True)

    class Meta:
        model = Contact
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = '__all__'


class InfoBlockSerializer(serializers.ModelSerializer):

    class Meta:
        model = InfoBlock
        fields = '__all__'


class BlogPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = BlogPost
        fields = '__all__'


class RequisiteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Requisite
        fields = '__all__'


class DeliverySerializer(serializers.ModelSerializer):

    class Meta:
        model = Delivery
        fields = '__all__'


class DenialOfResponsibilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = DenialOfResponsibility
        fields = '__all__'
