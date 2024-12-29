from django.db.models import Q, Subquery
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from services.pagination import DefaultPagination
from .filters import ProductFilter, ProductOrderingFilter
from .serializers import CatalogueSerializer, CategorySerializer, BrandSerializer, CountrySerializer, FormSerializer
from .serializers import ProductReviewSerializer, OrderSerializer
from .serializers import ProductSerializer, TreeCatalogueSerializer
from .models import Catalogue, Category, Brand, Country, Form, Product, ProductReview, Order


class CatalogueViewSet(ReadOnlyModelViewSet):
    queryset = Catalogue.objects.all()
    serializer_class = CatalogueSerializer
    pagination_class = DefaultPagination


class TreeCatalogueListAPIView(ListAPIView):
    queryset = Catalogue.objects.all()
    serializer_class = TreeCatalogueSerializer
    pagination_class = DefaultPagination


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = DefaultPagination

    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('parent', 'catalogue')


class BrandListAPIView(ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    pagination_class = DefaultPagination


class CountryListAPIView(ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class FormListAPIView(ListAPIView):
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    pagination_class = DefaultPagination


class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = DefaultPagination

    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        ProductOrderingFilter
    )
    filterset_class = ProductFilter
    search_fields = ('name', 'description')
    ordering_fields = ('id', 'price', 'name')

    @action(detail=True, methods=['get'], pagination_class=DefaultPagination)
    def similar(self, request, pk=None):
        instance = self.get_object()
        subquery = Product.objects.filter(
            Q(categories__in=instance.categories.values_list('id', flat=True))
        ).exclude(id=instance.id).values('id').distinct()

        queryset = Product.objects.filter(
            id__in=Subquery(subquery)
        ).order_by('?')
        serializer = self.get_serializer(queryset, many=True)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data, status=200)

    @action(detail=True, methods=['get'])
    def variations(self, request, pk=None):
        instance = self.get_object()
        base_product = instance.base_product if instance.is_variation else instance

        variations = {
            'current': {
                'id': instance.id,
                'flavor': instance.flavor,
                'dosage': instance.dosage,
                'quantity': instance.quantity,
                'in_stock': instance.status == Product.ProductStatus.in_stock,
                'product_id': instance.id
            },
            'flavors': [],
            'dosages': [],
            'quantities': []
        }

        if base_product:
            # Получаем все вариации базового продукта
            flavor_variations = base_product.variations.filter(variation_type='flavor')
            dosage_variations = base_product.variations.filter(variation_type='dosage')
            quantity_variations = base_product.variations.filter(variation_type='quantity')

            variations['flavors'] = [
                {
                    'id': v.id,
                    'flavor': v.flavor,
                    'in_stock': v.status == Product.ProductStatus.in_stock,
                    'product_id': v.id
                } for v in flavor_variations if v.id != instance.id
            ]

            variations['dosages'] = [
                {
                    'id': v.id,
                    'dosage': v.dosage,
                    'in_stock': v.status == Product.ProductStatus.in_stock,
                    'product_id': v.id
                } for v in dosage_variations if v.id != instance.id
            ]

            variations['quantities'] = [
                {
                    'id': v.id,
                    'quantity': v.quantity,
                    'in_stock': v.status == Product.ProductStatus.in_stock,
                    'product_id': v.id
                } for v in quantity_variations if v.id != instance.id
            ]

        return Response(variations)
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='sub_category_id', description='Sub category ID', required=False, type={'type': 'integer'}),
            OpenApiParameter(name='category_id', description='Category ID', required=False, type={'type': 'integer'}),
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        sub_category_id = request.query_params.get('sub_category_id', None)
        category_id = request.query_params.get('category_id', None)
        breadcrumbs: dict = {
            'sub_category_id': sub_category_id,
            'category_id': category_id,
        }
        serializer = self.get_serializer(instance, context={'request': request, 'breadcrumbs': breadcrumbs})
        data = serializer.data

        return Response(data, status=200)


class ProductReviewViewSet(ModelViewSet):
    queryset = ProductReview.objects.filter(is_allow=True)
    serializer_class = ProductReviewSerializer
    pagination_class = DefaultPagination
    http_method_names = ['get', 'post']

    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('product',)


class OrderCreateAPIView(CreateAPIView):
    serializer_class = OrderSerializer
    http_method_names = ['post']
