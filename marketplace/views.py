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
        similar_products = instance.similar_products.all()

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

        # Группируем все вариации
        flavors = similar_products.filter(flavor__isnull=False).distinct()
        if flavors.exists():
            variations['flavors'] = [{
                'id': prod.id,
                'flavor': prod.flavor,
                'in_stock': prod.status == Product.ProductStatus.in_stock,
                'product_id': prod.id
            } for prod in flavors]

        dosages = similar_products.filter(dosage__isnull=False).distinct()
        if dosages.exists():
            variations['dosages'] = [{
                'id': prod.id,
                'dosage': prod.dosage,
                'in_stock': prod.status == Product.ProductStatus.in_stock,
                'product_id': prod.id
            } for prod in dosages]

        quantities = similar_products.filter(quantity__isnull=False).distinct()
        if quantities.exists():
            variations['quantities'] = [{
                'id': prod.id,
                'quantity': prod.quantity,
                'in_stock': prod.status == Product.ProductStatus.in_stock,
                'product_id': prod.id
            } for prod in quantities]

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
