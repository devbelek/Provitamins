from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from services.pagination import DefaultPagination
from .serializers import BannerSerializer, FAQSerializer, TickerSerializer, ContactSerializer, ReviewSerializer
from .serializers import InfoBlockSerializer, BlogPostSerializer, RequisiteSerializer, DeliverySerializer
from .serializers import DenialOfResponsibilitySerializer
from .models import Banner, FAQ, Ticker, Contact, BlogPost, Requisite, InfoBlock, Review, Delivery
from .models import DenialOfResponsibility


class BannerListAPIView(ListAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    pagination_class = DefaultPagination


class FAQListAPIView(ListAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    pagination_class = DefaultPagination


class TickerListAPIView(ListAPIView):
    queryset = Ticker.objects.all()
    serializer_class = TickerSerializer
    pagination_class = DefaultPagination


class ContactListAPIView(ListAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    pagination_class = DefaultPagination


class ReviewListAPIView(ListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = DefaultPagination


class InfoBlockListAPIView(ListAPIView):
    queryset = InfoBlock.objects.all()
    serializer_class = InfoBlockSerializer
    pagination_class = DefaultPagination


class BlogPostViewSet(ReadOnlyModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    pagination_class = DefaultPagination


class RequisiteListAPIView(ListAPIView):
    queryset = Requisite.objects.all()
    serializer_class = RequisiteSerializer
    pagination_class = DefaultPagination


class DeliveryListAPIView(ListAPIView):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    pagination_class = DefaultPagination


class DenialOfResponsibilityListAPIView(ListAPIView):
    queryset = DenialOfResponsibility.objects.all()
    serializer_class = DenialOfResponsibilitySerializer
