from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny  # Добавляем это
from .serializers import Product1CSerializer
from .models import Product1C
from marketplace.models import Product


class Product1CView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        vendor_code = request.data.get('vendor_code')
        instance = Product1C.objects.filter(vendor_code=vendor_code).first()
        main_product = Product.objects.filter(vendor_code=vendor_code).first()

        # Создаем или обновляем с помощью сериализатора
        serializer = Product1CSerializer(instance, data=request.data, partial=True) if instance else Product1CSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            message = 'Товар успешно обновлен' if main_product else 'Товар успешно создан'
            return Response({
                'status': 'success',
                'message': message,
                'product_id': main_product.id if main_product else None
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)