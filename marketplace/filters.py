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
        """
        Фильтрация по каталогу:
        - Получаем все категории каталога
        - Получаем все их подкатегории
        - Фильтруем товары по всем этим категориям
        """
        try:
            catalogue = Catalogue.objects.get(id=value)
            # Получаем все корневые категории каталога
            root_categories = Category.objects.filter(catalogue=catalogue)
            # Получаем все подкатегории для каждой корневой категории
            all_categories = []
            for root_category in root_categories:
                all_categories.extend(root_category.get_descendants(include_self=True))
            return queryset.filter(categories__in=all_categories).distinct()
        except Catalogue.DoesNotExist:
            return queryset.none()

    def filter_category(self, queryset, name, value):
        """
        Фильтрация по категории:
        - Если категория принадлежит каталогу - это корневая категория
        - Если есть parent - это подкатегория
        """
        try:
            category = Category.objects.get(id=value)
            # Получаем все подкатегории включая текущую
            categories = category.get_descendants(include_self=True)
            return queryset.filter(categories__in=categories).distinct()
        except Category.DoesNotExist:
            return queryset.none()


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
