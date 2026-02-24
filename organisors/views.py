import logging
from django.core.mail import send_mail
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse
from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.contrib.auth import get_user_model

from leads.models import UserProfile, EmailVerificationToken
from activity_log.models import log_activity, ACTION_ORGANISOR_CREATED, ACTION_ORGANISOR_UPDATED, ACTION_ORGANISOR_DELETED
from .models import Organisor
from .forms import OrganisorModelForm, OrganisorCreateForm
from .mixins import AdminOnlyMixin, SelfProfileOnlyMixin
from django.contrib import messages

logger = logging.getLogger(__name__)
User = get_user_model()


class OrganisorListView(AdminOnlyMixin, generic.ListView):
    template_name = "organisors/organisor_list.html"
    context_object_name = "organisors"

    def get_queryset(self):
        queryset = Organisor.objects.exclude(user__is_superuser=True).select_related("user")
        search = (self.request.GET.get("q") or "").strip()
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__email__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q") or ""
        return context


class OrganisorCreateView(AdminOnlyMixin, generic.CreateView):
    template_name = "organisors/organisor_create.html"
    form_class = OrganisorCreateForm

    def get_success_url(self):
        return reverse("organisors:organisor-list")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_agent = False
        user.is_organisor = True
        user.email_verified = False
        
        try:
            with transaction.atomic():
                user.save()
                logger.info(f"User {user.username} created successfully")

                # Create UserProfile
                user_profile, created = UserProfile.objects.get_or_create(user=user)
                if created:
                    logger.info(f"UserProfile for {user.username} created successfully")

                # Create Organisor
                organisor = Organisor.objects.create(
                    user=user,
                    organisation=self.request.user.userprofile
                )
                logger.info(f"Organisor for {user.username} created successfully")
                log_activity(
                    self.request.user,
                    ACTION_ORGANISOR_CREATED,
                    object_type='organisor',
                    object_id=organisor.pk,
                    object_repr=f"Organisor: {user.email}",
                    organisation=self.request.user.userprofile,
                )

                # Email verification token
                verification_token = EmailVerificationToken.objects.create(user=user)
                self.send_verification_email(user, verification_token.token)
                messages.success(self.request, "Organisor created successfully.")
                
            return super().form_valid(form)
        except IntegrityError as e:
            logger.error(f"IntegrityError while creating organisor: {e}", exc_info=True)
            form.add_error(None, "An error occurred while creating the organisor. Please try again.")
            return self.form_invalid(form)
        except Exception as e:
            logger.error(f"Unexpected error while creating organisor: {e}", exc_info=True)
            form.add_error(None, "An unexpected error occurred. Please try again.")
            return self.form_invalid(form)

    def send_verification_email(self, user, token):
        verify_url = self.request.build_absolute_uri(reverse('verify-email', kwargs={'token': token}))
        subject = 'Darkenyas CRM - Organisor Account Verification'
        message = f"""
        Hello {user.first_name},
        
        You have been invited to be an organisor on Darkenyas CRM! Please click the link below to verify your email and activate your account:
        
        {verify_url}
        
        This link is valid for 24 hours.
        
        After verification, you can login with:
        Username: {user.username}
        Email: {user.email}
        
        As an organisor, you will be able to manage agents and access organizational features.
        
        If you didn't expect this invitation, you can ignore this email.
        
        Best regards,
        Darkenyas CRM Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class OrganisorDetailView(SelfProfileOnlyMixin, generic.DetailView):
    template_name = "organisors/organisor_detail.html"
    context_object_name = "organisor"
    
    def get_queryset(self):
        # Admin can see all organisors
        if self.is_admin_user(self.request.user):
            return Organisor.objects.all()
        # Organisor can only see themselves
        elif self.request.user.is_organisor:
            return Organisor.objects.filter(user=self.request.user)
        else:
            return Organisor.objects.none()
    
    def is_admin_user(self, user):
        """Check if user is admin/superuser."""
        return user.is_superuser


class OrganisorUpdateView(SelfProfileOnlyMixin, generic.UpdateView):
    template_name = "organisors/organisor_update.html"
    form_class = OrganisorModelForm
    context_object_name = 'organisor'
    
    def get_queryset(self):
        # Admin can update all organisors
        if self.is_admin_user(self.request.user):
            return Organisor.objects.all()
        # Organisor can only update themselves
        elif self.request.user.is_organisor:
            return Organisor.objects.filter(user=self.request.user)
        else:
            return Organisor.objects.none()

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        pk = self.kwargs['pk']
        try:
            organisor = queryset.get(pk=pk)
            return organisor.user  # Return User object for form
        except Organisor.DoesNotExist:
            raise Http404("Organisor not found.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the organisor object for template context
        organisor = Organisor.objects.get(pk=self.kwargs['pk'])
        context['organisor'] = organisor
        return context

    def get_success_url(self):
        return reverse("organisors:organisor-detail", kwargs={"pk": self.kwargs['pk']})

    def form_valid(self, form):
        response = super().form_valid(form)
        organisor = Organisor.objects.get(pk=self.kwargs['pk'])
        messages.success(self.request, "Organisor updated successfully.")
        log_activity(
            self.request.user,
            ACTION_ORGANISOR_UPDATED,
            object_type='organisor',
            object_id=organisor.pk,
            object_repr=f"Organisor: {organisor.user.email}",
            organisation=organisor.organisation,
        )
        return response
    
    def is_admin_user(self, user):
        """Check if user is admin/superuser."""
        return user.is_superuser


class OrganisorDeleteView(AdminOnlyMixin, generic.DeleteView):
    template_name = "organisors/organisor_delete.html"
    context_object_name = "organisor"
    
    def get_success_url(self):
        return reverse("organisors:organisor-list")

    def get_queryset(self):
        return Organisor.objects.all()
    
    def form_valid(self, form):
        # Get organisor and user
        organisor = self.get_object()
        user = organisor.user
        username = user.username
        org = organisor.organisation
        object_repr = f"Organisor: {user.email}"
        try:
            with transaction.atomic():
                log_activity(
                    self.request.user,
                    ACTION_ORGANISOR_DELETED,
                    object_type='organisor',
                    object_id=organisor.pk,
                    object_repr=object_repr,
                    organisation=org,
                )
                # Delete organisor first, then user
                organisor.delete()
                user.delete()
                
            logger.info(f"Organisor and User {username} deleted successfully")
            messages.success(self.request, "Organisor deleted successfully.")
            
        except Exception as e:
            logger.error(f"Error deleting organisor and user {username}: {e}")
            
        return HttpResponseRedirect(self.get_success_url())