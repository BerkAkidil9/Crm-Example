from django.urls import path
from .views import ProductAndStockListView,ProductAndStockDetailView,ProductAndStockCreateView,ProductAndStockUpdateView,ProductAndStockDeleteView

app_name = 'ProductsAndStock'  # Define the app name here

urlpatterns = [
    # Your URL patterns
    path('', ProductAndStockListView.as_view(), name="ProductAndStock-list"),
    path('<int:pk>/', ProductAndStockDetailView.as_view(), name="ProductAndStock-detail"),
    path('create/', ProductAndStockCreateView.as_view(), name="ProductAndStock-create"),
    path('<int:pk>/update/', ProductAndStockUpdateView.as_view(), name="ProductAndStock-update"),
    path('<int:pk>/delete/', ProductAndStockDeleteView.as_view(), name="ProductAndStock-delete"),

]