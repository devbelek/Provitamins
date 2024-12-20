import django_filters
from django.db.models import Case, When, IntegerField, F, Q
from rest_framework.filters import OrderingFilter

from .models import Product, Brand, Category, Form, Country, Catalogue


class ProductFilter(django_filters.FilterSet):
    price = django_filters.RangeFilter(method='custom_price_range_filter')
    catalogue = django_filters.NumberFilter(
        method='filter_catalogue',
    )
    category = django_filters.NumberFilter(
        method='filter_category',
    )
    sub_category = django_filters.ModelChoiceFilter(
        field_name='categories',
        queryset=Category.objects.all()
    )
    brand = django_filters.ModelMultipleChoiceFilter(
        field_name='brand',
        queryset=Brand.objects.all()
    )
    form = django_filters.ModelMultipleChoiceFilter(
        field_name='form',
        queryset=Form.objects.all()
    )
    country = django_filters.ModelMultipleChoiceFilter(
        field_name='manufacturer_country',
        queryset=Country.objects.all()
    )
    is_hit = django_filters.BooleanFilter()
    is_sale = django_filters.BooleanFilter()
    is_recommend = django_filters.BooleanFilter()
    id = django_filters.NumberFilter(method='filter_id')

    class Meta:
        model = Product
        fields = ('price', 'sub_category', 'brand', 'form', 'country', 'is_hit', 'is_sale', 'is_recommend', 'id')

    def filter_id(self, qs, name, value):
        return qs.filter(id__in=self.request.GET.getlist('id'))

    def custom_price_range_filter(self, queryset, name, value):
        queryset = queryset.annotate(
            effective_price=Case(
                When(sale_price__isnull=False, then=F('sale_price')),
                default=F('price'),
                output_field=IntegerField()
            )
        )
        if value.start and value.stop:
            return queryset.filter(effective_price__gte=value.start, effective_price__lte=value.stop)
        elif value.start:
            return queryset.filter(effective_price__gte=value.start)
        elif value.stop:
            return queryset.filter(effective_price__lte=value.stop)
        return queryset

    def filter_catalogue(self, queryset, name, value):
        return queryset.filter(Q(categories__catalogue=value) | Q(categories__parent__catalogue=value)).distinct()

    def filter_category(self, queryset, name, value):
        return queryset.filter(Q(categories=value) | Q(categories__parent=value)).distinct()


class ProductOrderingFilter(OrderingFilter):
    def get_ordering(self, request, queryset, view):
        params = request.query_params.get(self.ordering_param)
        if params:
            fields = [param.strip() for param in params.split(',')]
            return fields
        return self.get_default_ordering(view)

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view) or ()
        if 'price' in ordering or '-price' in ordering:
            queryset = queryset.annotate(
                prioritized_price=Case(
                    When(sale_price__isnull=False, then='sale_price'),
                    default='price',
                    output_field=IntegerField()
                )
            )
            queryset = queryset.order_by(*ordering, 'prioritized_price')
        else:
            queryset = queryset.order_by(*ordering)
        return queryset
