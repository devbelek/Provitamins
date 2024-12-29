from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny  # Добавляем это
from .serializers import Product1CSerializer
from .models import Product1C


class Product1CView(APIView):
    permission_classes = [AllowAny]  # Добавляем это
    authentication_classes = []  # И это

    def post(self, request):
        print("DEBUG: Request headers:", request.META)  # Добавляем для отладки
        vendor_code = request.data.get('vendor_code')
        instance = Product1C.objects.filter(vendor_code=vendor_code).first()

        if instance:
            serializer = Product1CSerializer(instance, data=request.data, partial=True)
        else:
            serializer = Product1CSerializer(data=request.data)

        if serializer.is_valid():
            product = serializer.save()
            return Response({
                'status': 'success',
                'message': 'Товар успешно обновлен' if instance else 'Товар успешно создан',
                'product_id': product.id
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)