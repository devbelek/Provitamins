from django.urls import path
from .views import Product1CView

urlpatterns = [
    path('products/', Product1CView.as_view(), name='1c-products'),
]