import logging
import random
from django.core.mail import send_mail
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse
from leads.models import Agent, UserProfile, User
from .forms import AgentModelForm
from .mixins import OrganisorAndLoginRequiredMixin
from django.db import transaction, IntegrityError
from django.contrib.auth import get_user_model
from django.http import Http404

logger = logging.getLogger(__name__)
User = get_user_model()

class AgentListView(OrganisorAndLoginRequiredMixin, generic.ListView):
    template_name = "agents/agent_list.html"

    def get_queryset(self):
        organisation = self.request.user.userprofile
        return Agent.objects.filter(organisation=organisation)
    
class AgentCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "agents/agent_create.html"
    form_class = AgentModelForm

    def get_success_url(self):
        return reverse("agents:agent-list")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_agent = True
        user.is_organisor = False
        user.set_password(User.objects.make_random_password())

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
                Agent.objects.create(
                    user=user,
                    organisation=self.request.user.userprofile
                )
                logger.info(f"Agent for {user.username} created successfully")

            send_mail(
                subject="You are invited to be an agent",
                message="You were added as an agent on DJCRM. Please come login to start working.",
                from_email="admin@test.com",
                recipient_list=[user.email]
            )
            return super().form_valid(form)
        except IntegrityError as e:
            logger.error(f"IntegrityError while creating agent: {e}", exc_info=True)
            form.add_error(None, "An error occurred while creating the agent. Please try again.")
            return self.form_invalid(form)
        except Exception as e:
            logger.error(f"Unexpected error while creating agent: {e}", exc_info=True)
            form.add_error(None, "An unexpected error occurred. Please try again.")
            return self.form_invalid(form)



    







class AgentDetailView(OrganisorAndLoginRequiredMixin, generic.DetailView):
    template_name = "agents/agent_detail.html"
    context_object_name = "agent"
    
    def get_queryset(self):
        organisation = self.request.user.userprofile
        logger.info(f"Fetching agents for organisation: {organisation}")
        return Agent.objects.filter(organisation=organisation)

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




    






class AgentUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "agents/agent_update.html"
    form_class = AgentModelForm
    context_object_name = 'agent'
    
    def get_queryset(self):
        organisation = self.request.user.userprofile
        logger.info(f"Fetching agents for organisation: {organisation}")
        return Agent.objects.filter(organisation=organisation)

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

    def get_initial(self):
      initial = super().get_initial()
      agent = self.get_object()
      user = agent.user  # Assuming the Agent model has a ForeignKey to User named 'user'
      initial.update({
        'email': user.email,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
    })
      return initial








    
class AgentDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "agents/agent_delete.html"
    context_object_name = "agent"
    
    def get_success_url(self):
        return reverse("agents:agent-list")

    def get_queryset(self):
        organisation = self.request.user.userprofile
        return Agent.objects.filter(organisation=organisation)