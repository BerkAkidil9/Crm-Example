from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.http import Http404
from leads.models import User

class AdminOnlyMixin(AccessMixin):
    """Only admin/superuser can access - for managing both agents and organisors."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("leads:lead-list")
        
        # Check if user is admin (first organisor or superuser)
        if not (request.user.is_superuser or self.is_admin_user(request.user)):
            return redirect("leads:lead-list")
            
        return super().dispatch(request, *args, **kwargs)
    
    def is_admin_user(self, user):
        """
        Check if user is admin/superuser.
        Uses Django's is_superuser flag for proper admin detection.
        """
        return user.is_superuser


class OrganisorAndAdminMixin(AccessMixin):
    """Allow organisors to see agents and their own profile."""
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


class SelfProfileOnlyMixin(AccessMixin):
    """Allow users to access only their own profile."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("leads:lead-list")
        
        # Admin can access any profile
        if request.user.is_superuser or self.is_admin_user(request.user):
            return super().dispatch(request, *args, **kwargs)
        
        # For detail/update views, check if accessing own profile
        if 'pk' in kwargs:
            try:
                from .models import Organisor
                organisor = Organisor.objects.get(pk=kwargs['pk'])
                if organisor.user != request.user:
                    raise Http404("You can only access your own profile.")
            except Organisor.DoesNotExist:
                raise Http404("Organisor not found.")
                
        return super().dispatch(request, *args, **kwargs)
    
    def is_admin_user(self, user):
        """
        Check if user is admin/superuser.
        Uses Django's is_superuser flag for proper admin detection.
        """
        return user.is_superuser
