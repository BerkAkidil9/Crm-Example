from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.http import Http404
from leads.models import Agent


class OrganisorAndLoginRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is an organisor or admin."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("leads:lead-list")
        
        # Admin can access everything
        if request.user.is_superuser or self.is_admin_user(request.user):
            return super().dispatch(request, *args, **kwargs)
            
        # Organisors can access
        if request.user.is_organisor:
            return super().dispatch(request, *args, **kwargs)
            
        return redirect("leads:lead-list")
    
    def is_admin_user(self, user):
        """
        Check if user is admin/superuser.
        Uses Django's is_superuser flag for proper admin detection.
        """
        return user.is_superuser


class AgentAndOrganisorLoginRequiredMixin(AccessMixin):
    """Allow both agents and organisors, but restrict agent access to their own data."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("leads:lead-list")
        
        # Admin can access everything
        if request.user.is_superuser or self.is_admin_user(request.user):
            return super().dispatch(request, *args, **kwargs)
        
        # Organisor'lar her şeyi görebilir
        if request.user.is_organisor:
            return super().dispatch(request, *args, **kwargs)
        
        # Agent'lar sadece kendi profillerini görebilir
        if request.user.is_agent:
            # Detail ve Update view'ları için pk kontrolü
            if 'pk' in kwargs:
                try:
                    agent = Agent.objects.get(pk=kwargs['pk'])
                    if agent.user != request.user:
                        raise Http404("You can only access your own profile.")
                except Agent.DoesNotExist:
                    raise Http404("Agent not found.")
            return super().dispatch(request, *args, **kwargs)
        
        # Ne organisor ne de agent ise redirect
        return redirect("leads:lead-list")
    
    def is_admin_user(self, user):
        """
        Check if user is admin/superuser.
        Uses Django's is_superuser flag for proper admin detection.
        """
        return user.is_superuser


class ProductsAndStockAccessMixin(AccessMixin):
    """Allow agents and organisors to access products from their organization."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("leads:lead-list")
        
        # Admin can access everything
        if request.user.is_superuser or self.is_admin_user(request.user):
            return super().dispatch(request, *args, **kwargs)
        
        # Organisors and agents can access
        if request.user.is_organisor or request.user.is_agent:
            return super().dispatch(request, *args, **kwargs)
        
        # Neither organisor nor agent - redirect
        return redirect("leads:lead-list")
    
    def is_admin_user(self, user):
        """
        Check if user is admin/superuser.
        Uses Django's is_superuser flag for proper admin detection.
        """
        return user.is_superuser