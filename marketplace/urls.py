from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CatalogueViewSet, CategoryViewSet, BrandListAPIView, CountryListAPIView, FormListAPIView
from .views import TreeCatalogueListAPIView, ProductViewSet, ProductReviewViewSet, OrderCreateAPIView

router = DefaultRouter()

router.register('products', ProductViewSet, basename='product')
router.register('catalogues', CatalogueViewSet, basename='catalogue')
router.register('categories', CategoryViewSet, basename='category')
router.register('product_reviews', ProductReviewViewSet, basename='product_review')

urlpatterns = [
    *router.urls,
    path('brands/', BrandListAPIView.as_view(), name='brand-list'),
    path('countries/', CountryListAPIView.as_view(), name='country-list'),
    path('forms/', FormListAPIView.as_view(), name='form-list'),
    path('tree_catalogues/', TreeCatalogueListAPIView.as_view(), name='tree-catalogue-list'),
    path('order/', OrderCreateAPIView.as_view(), name='order-create')
]
