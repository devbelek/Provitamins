from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import Product1CSerializer
from .models import Product1C


class Product1CView(APIView):
    def post(self, request):
        serializer = Product1CSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response({
                'status': 'success',
                'product_id': product.id
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)