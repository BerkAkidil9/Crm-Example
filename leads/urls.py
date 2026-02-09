from django.urls import path
from .views import (
    LeadListView, LeadDetailView, LeadActivityView, LeadCreateView, LeadUpdateView, LeadDeleteView, AssignAgentView, CategoryListView,
    CategoryDetailView, LeadCategoryUpdateView, get_agents_by_org
)

app_name = 'leads'

urlpatterns = [
    path('', LeadListView.as_view(), name="lead-list"),
    path('<int:pk>/', LeadDetailView.as_view(), name="lead-detail"),
    path('<int:pk>/update/', LeadUpdateView.as_view(), name="lead-update"),
    path('<int:pk>/delete/', LeadDeleteView.as_view(), name="lead-delete"),
    path('create/', LeadCreateView.as_view(), name="lead-create"),
    path('<int:pk>/assign-agent/', AssignAgentView.as_view(), name="assign-agent"),
    path('<int:pk>/category/', LeadCategoryUpdateView.as_view(), name="lead-category-update"),
    path('<int:pk>/activity/', LeadActivityView.as_view(), name="lead-activity"),
    path('categories/', CategoryListView.as_view(), name="category-list"),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name="category-detail"),
    path('get-agents-by-org/<int:org_id>/', get_agents_by_org, name="get-agents-by-org"),
]