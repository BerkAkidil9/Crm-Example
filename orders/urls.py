from django.urls import path
from .views import OrderListView, OrderDetailView, OrderCreateView, OrderUpdateView, OrderDeleteView, OrderCancelView

app_name = 'orders'  # Define the app name here

urlpatterns = [
    path('', OrderListView.as_view(), name="order-list"),
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('order-create/', OrderCreateView.as_view(), name='order-create'),
    path('order-update/<int:pk>/', OrderUpdateView.as_view(), name='order-update'),
    path('order-delete/<int:pk>/', OrderDeleteView.as_view(), name='order-delete'),
    path('order-cancel/<int:pk>/', OrderCancelView.as_view(), name='order-cancel'),
]