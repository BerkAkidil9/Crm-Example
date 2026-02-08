from django.urls import path
from .views import ProductAndStockListView, ProductAndStockDetailView, ProductAndStockCreateView, ProductAndStockUpdateView, ProductAndStockDeleteView, get_subcategories, BulkPriceUpdateView, SalesDashboardView, ProductChartsView

app_name = 'ProductsAndStock'  # Define the app name here

urlpatterns = [
    # Your URL patterns
    path('', ProductAndStockListView.as_view(), name="ProductAndStock-list"),
    path('dashboard/', SalesDashboardView.as_view(), name="sales-dashboard"),
    path('<int:pk>/', ProductAndStockDetailView.as_view(), name="ProductAndStock-detail"),
    path('create/', ProductAndStockCreateView.as_view(), name="ProductAndStock-create"),
    path('<int:pk>/update/', ProductAndStockUpdateView.as_view(), name="ProductAndStock-update"),
    path('<int:pk>/delete/', ProductAndStockDeleteView.as_view(), name="ProductAndStock-delete"),
    path('bulk-price-update/', BulkPriceUpdateView.as_view(), name="bulk-price-update"),
    path('charts/', ProductChartsView.as_view(), name="product-charts"),
    path('get-subcategories/', get_subcategories, name="get-subcategories"),

]