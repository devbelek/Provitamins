from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import BannerListAPIView, TickerListAPIView, FAQListAPIView, ContactListAPIView, DeliveryListAPIView
from .views import ReviewListAPIView, InfoBlockListAPIView, BlogPostViewSet, RequisiteListAPIView
from .views import DenialOfResponsibilityListAPIView

router = DefaultRouter()

router.register('blog_posts', BlogPostViewSet, basename='blog-post')

urlpatterns = [
    *router.urls,
    path('banner/', BannerListAPIView.as_view(), name='banner-list'),
    path('tickers/', TickerListAPIView.as_view(), name='ticker-list'),
    path('faqs/', FAQListAPIView.as_view(), name='faq-list'),
    path('contacts/', ContactListAPIView.as_view(), name='contact-list'),
    path('reviews/', ReviewListAPIView.as_view(), name='review-list'),
    path('info_blocks/', InfoBlockListAPIView.as_view(), name='info-block-list'),
    path('requisites/', RequisiteListAPIView.as_view(), name='requisite-list'),
    path('deliveries/', DeliveryListAPIView.as_view(), name='delivery-list'),
    path('denial/', DenialOfResponsibilityListAPIView.as_view(), name='denial-list')
]
