import logging
import random
from django.core.mail import send_mail
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse
from leads.models import Agent, UserProfile, User, EmailVerificationToken
from .forms import AgentModelForm, AgentCreateForm, AdminAgentCreateForm
from .mixins import OrganisorAndLoginRequiredMixin, AgentAndOrganisorLoginRequiredMixin
from django.db import transaction, IntegrityError
from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponseRedirect

logger = logging.getLogger(__name__)
User = get_user_model()

class AgentListView(OrganisorAndLoginRequiredMixin, generic.ListView):
    template_name = "agents/agent_list.html"

    def get_queryset(self):
        # Admin can see all agents
        if self.request.user.is_superuser:
            return Agent.objects.all()
        # Organisors see agents in their organisation
        else:
            organisation = self.request.user.userprofile
            return Agent.objects.filter(organisation=organisation)
    
class AgentCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "agents/agent_create.html"
    
    def get_form_class(self):
        user = self.request.user
        if user.is_superuser:
            return AdminAgentCreateForm
        else:
            return AgentCreateForm

    def get_success_url(self):
        return reverse("agents:agent-list")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_agent = True
        user.is_organisor = False
        user.email_verified = False  # Email doğrulanmamış olarak başlat
        # Şifre form'da set ediliyor, burada tekrar set etmeye gerek yok

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
                    # Admin için form'dan seçilen organizasyonu kullan
                    selected_organisation = form.cleaned_data.get('organisation')
                    Agent.objects.create(
                        user=user,
                        organisation=selected_organisation
                    )
                else:
                    # Organisor için kendi organizasyonunu kullan
                    Agent.objects.create(
                        user=user,
                        organisation=self.request.user.userprofile
                    )
                logger.info(f"Agent for {user.username} created successfully")

                # Email doğrulama token'ı oluştur
                verification_token = EmailVerificationToken.objects.create(user=user)
                
                # Email gönder
                self.send_verification_email(user, verification_token.token)
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
        subject = 'DJ CRM - Agent Account Verification'
        message = f"""
        Hello {user.first_name},
        
        You have been invited to be an agent on DJ CRM! Please click the link below to verify your email and activate your account:
        
        http://127.0.0.1:8000/verify-email/{token}/
        
        This link is valid for 24 hours.
        
        After verification, you can login with:
        Username: {user.username}
        Email: {user.email}
        
        If you didn't expect this invitation, you can ignore this email.
        
        Best regards,
        DJ CRM Team
        """
        
        send_mail(
            subject,
            message,
            'admin@test.com',
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
        # Organisor ise tüm agent'ları görebilir
        elif self.request.user.is_organisor:
            organisation = self.request.user.userprofile
            logger.info(f"Fetching agents for organisation: {organisation}")
            return Agent.objects.filter(organisation=organisation)
        # Agent ise sadece kendisini görebilir
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
    form_class = AgentModelForm
    context_object_name = 'agent'
    
    def get_queryset(self):
        # Admin can update all agents
        if self.request.user.is_superuser:
            logger.info(f"Admin fetching all agents for update")
            return Agent.objects.all()
        # Organisor ise tüm agent'ları güncelleyebilir
        elif self.request.user.is_organisor:
            organisation = self.request.user.userprofile
            logger.info(f"Fetching agents for organisation: {organisation}")
            return Agent.objects.filter(organisation=organisation)
        # Agent ise sadece kendisini güncelleyebilir
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
        # Agent'ı al
        agent = self.get_object()
        user = agent.user
        username = user.username
        
        try:
            with transaction.atomic():
                # Önce Agent'ı sil
                agent.delete()
                # Sonra ilişkili User'ı da sil
                user.delete()
                
            logger.info(f"Agent and User {username} deleted successfully")
            
        except Exception as e:
            logger.error(f"Error deleting agent and user {username}: {e}")
            
        return HttpResponseRedirect(self.get_success_url())