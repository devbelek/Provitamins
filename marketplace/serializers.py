from rest_framework import serializers


from .models import Category, Catalogue, Brand, Country, Form, Product, ProductImage, ProductReview, Order, OrderItem
from marketplace.services.telegram import bot


class CatalogueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Catalogue
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        exclude = ('product',)


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    sub_category_name = serializers.CharField(read_only=True)
    sub_category_id = serializers.IntegerField(read_only=True)
    category_name = serializers.CharField(read_only=True)
    category_id = serializers.IntegerField(read_only=True)
    catalogue_name = serializers.CharField(read_only=True)
    catalogue_id = serializers.IntegerField(read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    form_name = serializers.CharField(source='form.name', read_only=True, allow_blank=True, allow_null=True)
    country_name = serializers.CharField(source='manufacturer_country.name', read_only=True)
    similar_products = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_similar_products(self, obj):
        """Получение информации о похожих товарах"""
        return [{
            'id': product.id,
            'name': product.name,
            'flavor': product.flavor,
            'dosage': product.dosage,
            'price': product.price,
            'sale_price': product.sale_price,
            'current_price': product.current_price,
            'status': product.status,
            'images': ProductImageSerializer(product.images.all(), many=True).data
        } for product in obj.similar_products.all()]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        breadcrumbs = self.context.get('breadcrumbs')
        if breadcrumbs:
            sub_category_id = breadcrumbs.get('sub_category_id', None)
            category_id = breadcrumbs.get('category_id', None)
            if sub_category_id:
                sub_category = Category.objects.filter(id=sub_category_id).first()
                if sub_category:
                    data['sub_category_id'] = sub_category.id
                    data['sub_category_name'] = sub_category.name
                    if sub_category.level == 0:
                        catalogue = sub_category.catalogue
                        data['catalogue_name'] = catalogue.name
                        data['catalogue_id'] = catalogue.id
            if category_id:
                category = Category.objects.filter(id=category_id).first()
                if category:
                    data['category_id'] = category.id
                    data['category_name'] = category.name
                    if category.level == 0:
                        catalogue = category.catalogue
                        data['catalogue_name'] = catalogue.name
                        data['catalogue_id'] = catalogue.id
        return data


class TreeCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(source="get_children")

    class Meta:
        model = Category
        fields = '__all__'

    def get_children(self, obj):
        if obj.level == 0:
            children_qs = Category.objects.filter(parent=obj)
            serializer = TreeCategorySerializer(children_qs, many=True, context=self.context)
            return serializer.data
        return None


class TreeCatalogueSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(source="get_children")

    class Meta:
        model = Catalogue
        fields = '__all__'

    def get_children(self, obj):
        children_qs = Category.objects.filter(catalogue=obj)
        serializer = TreeCategorySerializer(children_qs, many=True, context=self.context)
        return serializer.data


class ProductReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductReview
        exclude = ('is_allow',)


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ('product', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    date_created = serializers.DateTimeField(format='%d.%m.%Y %H:%M', read_only=True)
    items = OrderItemSerializer(many=True)
    total_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        exclude = ('status',)

    def create(self, validated_data):
        items = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item in items:
            OrderItem.objects.create(order=order, **item)
        order.total_price = sum([item.product.current_price * item.quantity for item in order.items.all()])
        order.save()
        bot.send_message(order)
        return order