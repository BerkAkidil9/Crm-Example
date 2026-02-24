import logging
import random
from django.core.mail import send_mail
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse
from django.conf import settings
from leads.models import Agent, UserProfile, User, EmailVerificationToken
from activity_log.models import log_activity, ACTION_AGENT_CREATED, ACTION_AGENT_UPDATED, ACTION_AGENT_DELETED
from .forms import AgentModelForm, AgentCreateForm, AdminAgentCreateForm, AdminAgentModelForm, OrganisorAgentCreateForm, OrganisorAgentModelForm
from .mixins import OrganisorAndLoginRequiredMixin, AgentAndOrganisorLoginRequiredMixin
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages

logger = logging.getLogger(__name__)
User = get_user_model()

class AgentListView(OrganisorAndLoginRequiredMixin, generic.ListView):
    template_name = "agents/agent_list.html"

    def get_queryset(self):
        # Admin can see all agents
        if self.request.user.is_superuser:
            queryset = Agent.objects.all().select_related("user", "organisation")
        else:
            organisation = self.request.user.userprofile
            queryset = Agent.objects.filter(organisation=organisation).select_related("user", "organisation")

        # Search: username, first_name, last_name, email
        search = (self.request.GET.get("q") or "").strip()
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__email__icontains=search)
            )

        # Admin-only: filter by organisation
        if self.request.user.is_superuser:
            org_id = self.request.GET.get("organisation")
            if org_id:
                queryset = queryset.filter(organisation_id=org_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context["filter_organisations"] = UserProfile.objects.filter(user__is_organisor=True, user__is_superuser=False).order_by("user__username")
            context["current_organisation_id"] = self.request.GET.get("organisation") or ""
        context["search_query"] = self.request.GET.get("q") or ""
        return context
    
class AgentCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "agents/agent_create.html"
    
    def get_form_class(self):
        user = self.request.user
        if user.is_superuser:
            return AdminAgentCreateForm
        if user.is_organisor:
            return OrganisorAgentCreateForm
        return AgentCreateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method != 'POST':
            kwargs.pop('data', None)
            kwargs.pop('files', None)
        else:
            kwargs.setdefault('files', self.request.FILES)
        return kwargs

    def get_success_url(self):
        return reverse("agents:agent-list")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_agent = True
        user.is_organisor = False
        user.email_verified = False  # Start with email unverified
        # Password is set in the form, no need to set it here again

        try:
            with transaction.atomic():
                user.save()
                logger.info(f"User {user.username} created successfully")

                # Ensure UserProfile is only created if it doesn't already exist
                user_profile, created = UserProfile.objects.get_or_create(user=user)
                if created:
                    logger.info(f"UserProfile for {user.username} created successfully")
                else:
                    logger.info(f"UserProfile for {user.username} already exists")

                # Create Agent
                if self.request.user.is_superuser:
                    # For admin: use organisation selected in the form
                    selected_organisation = form.cleaned_data.get('organisation')
                    agent = Agent.objects.create(
                        user=user,
                        organisation=selected_organisation
                    )
                    org_for_log = selected_organisation
                else:
                    # For organisor: use their own organisation
                    agent = Agent.objects.create(
                        user=user,
                        organisation=self.request.user.userprofile
                    )
                    org_for_log = self.request.user.userprofile
                logger.info(f"Agent for {user.username} created successfully")
                log_activity(
                    self.request.user,
                    ACTION_AGENT_CREATED,
                    object_type='agent',
                    object_id=agent.pk,
                    object_repr=f"Agent: {user.email}",
                    organisation=org_for_log,
                )

                # Create email verification token
                verification_token = EmailVerificationToken.objects.create(user=user)
                
                # Send email
                self.send_verification_email(user, verification_token.token)
                messages.success(self.request, "Agent created successfully.")
            return super().form_valid(form)
        except IntegrityError as e:
            logger.error(f"IntegrityError while creating agent: {e}", exc_info=True)
            form.add_error(None, "An error occurred while creating the agent. Please try again.")
            return self.form_invalid(form)
        except Exception as e:
            logger.error(f"Unexpected error while creating agent: {e}", exc_info=True)
            form.add_error(None, "An unexpected error occurred. Please try again.")
            return self.form_invalid(form)

    def send_verification_email(self, user, token):
        verify_url = self.request.build_absolute_uri(reverse('verify-email', kwargs={'token': token}))
        subject = 'Darkenyas CRM - Agent Account Verification'
        message = f"""
        Hello {user.first_name},
        
        You have been invited to be an agent on Darkenyas CRM! Please click the link below to verify your email and activate your account:
        
        {verify_url}
        
        This link is valid for 24 hours.
        
        After verification, you can login with:
        Username: {user.username}
        Email: {user.email}
        
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



    







class AgentDetailView(AgentAndOrganisorLoginRequiredMixin, generic.DetailView):
    template_name = "agents/agent_detail.html"
    context_object_name = "agent"
    
    def get_queryset(self):
        # Admin can see all agents
        if self.request.user.is_superuser:
            logger.info(f"Admin fetching all agents")
            return Agent.objects.all()
        # Organisor can see all agents
        elif self.request.user.is_organisor:
            organisation = self.request.user.userprofile
            logger.info(f"Fetching agents for organisation: {organisation}")
            return Agent.objects.filter(organisation=organisation)
        # Agent can only see themselves
        elif self.request.user.is_agent:
            logger.info(f"Fetching agent profile for user: {self.request.user.username}")
            return Agent.objects.filter(user=self.request.user)
        else:
            return Agent.objects.none()

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        pk = self.kwargs['pk']
        logger.info(f"Attempting to fetch agent with pk={pk}")
        try:
            agent = queryset.get(pk=pk)
            logger.info(f"Found agent: {agent}")
            return agent
        except Agent.DoesNotExist:
            logger.error(f"Agent with pk={pk} does not exist in the organization {self.request.user.userprofile}")
            raise Http404("Agent matching query does not exist.")




    






class AgentUpdateView(AgentAndOrganisorLoginRequiredMixin, generic.UpdateView):
    template_name = "agents/agent_update.html"
    context_object_name = 'agent'

    def get_form_class(self):
        if self.request.user.is_superuser:
            return AdminAgentModelForm
        if self.request.user.is_organisor:
            return OrganisorAgentModelForm
        return AgentModelForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method != 'POST':
            kwargs.pop('data', None)
            kwargs.pop('files', None)
        else:
            kwargs.setdefault('files', self.request.FILES)
        # Ensure form is bound to the agent's User instance so fields are pre-filled
        if 'instance' not in kwargs and self.request.method != 'POST':
            try:
                agent = self.get_queryset().get(pk=self.kwargs['pk'])
                kwargs['instance'] = agent.user
            except Agent.DoesNotExist:
                pass
        # For admin: pass agent so form can show/update organisation
        if self.request.user.is_superuser:
            try:
                kwargs['agent'] = self.get_queryset().get(pk=self.kwargs['pk'])
            except Agent.DoesNotExist:
                pass
        return kwargs

    def get_queryset(self):
        # Admin can update all agents
        if self.request.user.is_superuser:
            logger.info(f"Admin fetching all agents for update")
            return Agent.objects.all()
        # Organisor can update all agents
        elif self.request.user.is_organisor:
            organisation = self.request.user.userprofile
            logger.info(f"Fetching agents for organisation: {organisation}")
            return Agent.objects.filter(organisation=organisation)
        # Agent can only update themselves
        elif self.request.user.is_agent:
            logger.info(f"Fetching agent profile for user: {self.request.user.username}")
            return Agent.objects.filter(user=self.request.user)
        else:
            return Agent.objects.none()

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        pk = self.kwargs['pk']
        logger.info(f"Attempting to fetch agent with pk={pk}")
        try:
            agent = queryset.get(pk=pk)
            logger.info(f"Found agent: {agent}")
            return agent.user  # Return the User object instead of Agent
        except Agent.DoesNotExist:
            logger.error(f"Agent with pk={pk} does not exist in the organization {self.request.user.userprofile}")
            raise Http404("Agent matching query does not exist.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the agent object for template context using the same logic as get_queryset
        if self.request.user.is_superuser:
            agent_queryset = Agent.objects.all()
        elif self.request.user.is_organisor:
            agent_queryset = Agent.objects.filter(organisation=self.request.user.userprofile)
        elif self.request.user.is_agent:
            agent_queryset = Agent.objects.filter(user=self.request.user)
        else:
            agent_queryset = Agent.objects.none()
        
        agent = agent_queryset.get(pk=self.kwargs['pk'])
        context['agent'] = agent
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        try:
            agent = self.get_queryset().get(pk=self.kwargs['pk'])
            # Admin can change agent's organisation
            if self.request.user.is_superuser and hasattr(form, 'cleaned_data') and 'organisation' in form.cleaned_data:
                agent.organisation = form.cleaned_data['organisation']
                agent.save()
            messages.success(self.request, "Agent updated successfully.")
            log_activity(
                self.request.user,
                ACTION_AGENT_UPDATED,
                object_type='agent',
                object_id=agent.pk,
                object_repr=f"Agent: {agent.user.email}",
                organisation=agent.organisation,
            )
        except Agent.DoesNotExist:
            pass
        return response

    def get_success_url(self):
        return reverse("agents:agent-detail", kwargs={"pk": self.kwargs['pk']})








    
class AgentDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "agents/agent_delete.html"
    context_object_name = "agent"
    
    def get_success_url(self):
        return reverse("agents:agent-list")

    def get_queryset(self):
        # Admin can delete all agents
        if self.request.user.is_superuser:
            return Agent.objects.all()
        # Organisors can delete agents in their organisation
        else:
            organisation = self.request.user.userprofile
            return Agent.objects.filter(organisation=organisation)
    
    def form_valid(self, form):
        # Get the agent
        agent = self.get_object()
        user = agent.user
        username = user.username
        org = agent.organisation
        object_repr = f"Agent: {user.email}"
        try:
            with transaction.atomic():
                log_activity(
                    self.request.user,
                    ACTION_AGENT_DELETED,
                    object_type='agent',
                    object_id=agent.pk,
                    object_repr=object_repr,
                    organisation=org,
                )
                # Delete the agent first
                agent.delete()
                # Then delete the related User
                user.delete()
                
                logger.info(f"Agent and User {username} deleted successfully")
                messages.success(self.request, "Agent deleted successfully.")
            
        except Exception as e:
            logger.error(f"Error deleting agent and user {username}: {e}")
            
        return HttpResponseRedirect(self.get_success_url())