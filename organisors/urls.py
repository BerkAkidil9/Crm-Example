from django.urls import path
from .views import (
    OrganisorListView, 
    OrganisorCreateView, 
    OrganisorDetailView, 
    OrganisorUpdateView, 
    OrganisorDeleteView
)

app_name = 'organisors'

urlpatterns = [
    path('', OrganisorListView.as_view(), name='organisor-list'),
    path('create/', OrganisorCreateView.as_view(), name='organisor-create'),
    path('<int:pk>/', OrganisorDetailView.as_view(), name='organisor-detail'),
    path('<int:pk>/update/', OrganisorUpdateView.as_view(), name='organisor-update'),
    path('<int:pk>/delete/', OrganisorDeleteView.as_view(), name='organisor-delete'),
]
