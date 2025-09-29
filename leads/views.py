from typing import Any
from django.core.mail import send_mail
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, JsonResponse
from django.views import generic
from django.contrib import messages
from django.conf import settings
from django.db import models
from agents.mixins import OrganisorAndLoginRequiredMixin
from .models import Lead, Agent, Category, UserProfile, EmailVerificationToken, SourceCategory, ValueCategory
from .forms import LeadForm, LeadModelForm, CustomUserCreationForm, AssignAgentForm, LeadCategoryUpdateForm, CustomAuthenticationForm, AdminLeadModelForm





class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'
    
    def form_invalid(self, form):
        # Sadece gerçek form submission'da hata göster
        if self.request.method == 'POST':
            username = form.cleaned_data.get('username', '')
            if username:
                try:
                    from django.db import models
                    from .models import User
                    user = User.objects.filter(
                        models.Q(username__iexact=username) | models.Q(email__iexact=username)
                    ).first()
                    
                    if user and not user.email_verified:
                        messages.error(self.request, "Please verify your account by clicking the verification link sent to your email address.")
                        return super().form_invalid(form)
                except:
                    pass
            
            # Sadece username ve password dolu ise hata mesajı göster
            if username and form.cleaned_data.get('password', ''):
                messages.error(self.request, "Invalid username/email or password.")
        
        return super().form_invalid(form)

class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse("verify-email-sent")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.email = form.cleaned_data.get('email')
        user.first_name = form.cleaned_data.get('first_name')
        user.last_name = form.cleaned_data.get('last_name')
        user.is_organisor = True  # Set the user as an organisor (company owner)
        user.is_agent = False
        user.email_verified = False  # Email doğrulanmamış olarak başlat
        user.save()

        # Create UserProfile and Organisor
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        from organisors.models import Organisor
        Organisor.objects.create(user=user, organisation=user_profile)

        # Email doğrulama token'ı oluştur
        verification_token = EmailVerificationToken.objects.create(user=user)
        
        # Email gönder
        self.send_verification_email(user, verification_token.token)

        return super().form_valid(form)
    
    def send_verification_email(self, user, token):
        subject = 'DJ CRM - Email Verification'
        message = f"""
        Hello {user.first_name},
        
        Welcome to DJ CRM! Please click the link below to activate your account:
        
        http://127.0.0.1:8000/verify-email/{token}/
        
        This link is valid for 24 hours.
        
        If you didn't perform this action, you can ignore this email.
        
        Best regards,
        DJ CRM Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )



class EmailVerificationSentView(generic.TemplateView):
    template_name = "registration/verify_email_sent.html"

class EmailVerificationView(generic.View):
    def get(self, request, token):
        try:
            verification_token = EmailVerificationToken.objects.get(token=token)
            
            if verification_token.is_used:
                messages.error(request, "This verification link has already been used.")
                return redirect('verify-email-failed')
            
            if verification_token.is_expired():
                messages.error(request, "This verification link has expired.")
                return redirect('verify-email-failed')
            
            # Verify email
            user = verification_token.user
            user.email_verified = True
            user.save()
            
            # Mark token as used
            verification_token.is_used = True
            verification_token.save()
            
            messages.success(request, "Your email has been successfully verified! You can now login.")
            return redirect('login')
            
        except EmailVerificationToken.DoesNotExist:
            messages.error(request, "Invalid verification link.")
            return redirect('verify-email-failed')

class EmailVerificationFailedView(generic.TemplateView):
    template_name = "registration/verify_email_failed.html"

class LandingPageView(generic.TemplateView):
	template_name = "landing.html"

def landing_page(request):
	return render(request, "landing.html")

class LeadListView(LoginRequiredMixin, generic.ListView):
	template_name = "leads/lead_list.html"
	context_object_name = "leads"

	def get_queryset(self):
		user = self.request.user

		# Admin can see all leads
		if user.is_superuser:
			queryset = Lead.objects.filter(agent__isnull=False)
		elif user.is_organisor:
			queryset = Lead.objects.filter(organisation=user.userprofile, agent__isnull=False)
		else:
			queryset = Lead.objects.filter(organisation=user.agent.organisation, agent__isnull=False)
			queryset = queryset.filter(agent__user=user)
		return queryset
	
	def get_context_data(self, **kwargs):
		context = super(LeadListView, self).get_context_data(**kwargs)
		user = self.request.user

		# Admin can see all unassigned leads
		if user.is_superuser:
			queryset = Lead.objects.filter(agent__isnull=True)
			context.update({
				"unassigned_leads": queryset
			})
		elif user.is_organisor:
			queryset = Lead.objects.filter(organisation=user.userprofile, agent__isnull=True)
			context.update({
				"unassigned_leads": queryset
			})
		return context

def lead_list(request):
   leads = Lead.objects.all()
   context = {
	  "lead": leads
   }
   return render(request, "leads/lead_list.html", context)

class LeadDetailView(LoginRequiredMixin, generic.DetailView):
	template_name = "leads/lead_detail.html"
	context_object_name = "lead"

	def get_queryset(self):
		user = self.request.user

		# Admin can see all leads
		if user.is_superuser or user.id == 1 or user.username == 'berk':
			queryset = Lead.objects.all()
		elif user.is_organisor:
			queryset = Lead.objects.filter(organisation=user.userprofile)
		else:
			queryset = Lead.objects.filter(organisation=user.agent.organisation)
			queryset = queryset.filter(agent__user=user)
		return queryset

def lead_detail(request, pk):
	lead = Lead.objects.get(id=pk)
	context = {
		"lead": lead
	}
	return render(request, "leads/lead_detail.html", context)

class LeadCreateView(OrganisorAndLoginRequiredMixin, generic.CreateView):
	template_name = "leads/lead_create.html"
	
	def get_form_class(self):
		user = self.request.user
		if user.is_superuser:
			return AdminLeadModelForm
		else:
			return LeadModelForm

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['request'] = self.request
		return kwargs

	def get_success_url(self):
		return reverse("leads:lead-list")
	
	def form_valid(self, form):
		lead = form.save(commit=False)
		user = self.request.user
		
		if user.is_superuser:
			# Admin için form'dan seçilen organizasyonu kullan
			if hasattr(form, 'cleaned_data') and 'organisation' in form.cleaned_data:
				lead.organisation = form.cleaned_data['organisation']
			else:
				# Fallback - ilk organizasyonu kullan
				from leads.models import UserProfile
				default_org = UserProfile.objects.filter(user__is_organisor=True, user__is_superuser=False).first()
				if default_org:
					lead.organisation = default_org
		else:
			# Organisors use their own organisation
			lead.organisation = user.userprofile
			
		lead.save()
		send_mail(
			subject="A lead has been created",
			message="Go to the site to see the new lead",
			from_email="test@test.com",
			recipient_list=["test2@test.com"]
		)
		return super(LeadCreateView, self).form_valid(form)

def lead_create(request):
	form = LeadModelForm()
	if request.method == "POST":
		form = LeadModelForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect("/leads")
	context = {
		"form": form
	}
	return render(request, "leads/lead_create.html", context)

class LeadUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
	template_name = "leads/lead_update.html"
	
	def get_form_class(self):
		user = self.request.user
		if user.is_superuser:
			return AdminLeadModelForm
		else:
			return LeadModelForm

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['request'] = self.request
		return kwargs

	def get_queryset(self):
		user = self.request.user
		# Admin can update all leads
		if user.is_superuser:
			return Lead.objects.all()
		# Organisors can update their own leads
		else:
			return Lead.objects.filter(organisation=user.userprofile)

	def get_success_url(self):
		return reverse("leads:lead-list")

def lead_update(request, pk):
	lead = Lead.objects.get(id=pk)
	form = LeadModelForm(instance=lead)
	if request.method == "POST":
		form = LeadModelForm(request.POST, instance=lead)
		if form.is_valid():
			form.save()
			return redirect("/leads")
	context = {
		"form": form,
		"lead": lead
	}
	return render(request, "leads/lead_update.html", context)

class LeadDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
	template_name = "leads/lead_delete.html"
	
	def get_queryset(self):
		user = self.request.user
		# Admin can delete all leads
		if user.is_superuser or user.id == 1 or user.username == 'berk':
			return Lead.objects.all()
		# Organisors can delete their own leads
		else:
			return Lead.objects.filter(organisation=user.userprofile)

	def get_success_url(self):
		return reverse("leads:lead-list")

def lead_delete(request, pk):
	lead = Lead.objects.get(id=pk)
	lead.delete()
	return redirect("/leads")

class AssignAgentView(OrganisorAndLoginRequiredMixin, generic.FormView):
	template_name = "leads/assign_agent.html"
	form_class = AssignAgentForm

	def get_form_kwargs(self, **kwargs):
		kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
		kwargs.update({
			"request": self.request
		})
		return kwargs

	def get_success_url(self):
		return reverse("leads:lead-list")
	
	def form_valid(self, form):
		agent = form.cleaned_data["agent"]
		lead = Lead.objects.get(id=self.kwargs["pk"])
		lead.agent = agent
		lead.save()
		return super(AssignAgentView, self).form_valid(form)
	
from django.db.models import Count

class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/category_list.html"
    context_object_name = "category_list"

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user

        # Get Categories with filtering for admin
        if user.is_superuser or user.id == 1 or user.username == 'berk':
            # Get filter parameters
            selected_org_id = self.request.GET.get('organization')
            selected_agent_id = self.request.GET.get('agent')
            
            # Get all organizations for dropdown (only real organisors, exclude admin)
            all_organizations = UserProfile.objects.filter(
                user__is_organisor=True, 
                user__is_superuser=False
            ).exclude(user__id=1).exclude(user__username='berk')
            
            # Get agents based on selected organization
            if selected_org_id:
                try:
                    selected_org = UserProfile.objects.get(id=selected_org_id)
                    agents = Agent.objects.filter(organisation=selected_org)
                except UserProfile.DoesNotExist:
                    selected_org = None
                    agents = Agent.objects.none()
            else:
                selected_org = None
                agents = Agent.objects.all()
            
            # Get selected agent
            selected_agent = None
            if selected_agent_id:
                try:
                    selected_agent = Agent.objects.get(id=selected_agent_id)
                except Agent.DoesNotExist:
                    selected_agent = None
            
            # Filter categories based on selections
            if selected_agent:
                # Show categories for specific agent's leads
                source_categories = SourceCategory.objects.filter(
                    organisation=selected_agent.organisation
                ).annotate(
                    lead_count=Count('leads', filter=models.Q(leads__agent=selected_agent))
                )
                value_categories = ValueCategory.objects.filter(
                    organisation=selected_agent.organisation
                ).annotate(
                    lead_count=Count('leads', filter=models.Q(leads__agent=selected_agent))
                )
                filter_title = f"Categories for Agent: {selected_agent.user.username} ({selected_agent.organisation.user.username})"
                
            elif selected_org:
                # Show categories for specific organization
                source_categories = SourceCategory.objects.filter(organisation=selected_org).annotate(lead_count=Count('leads'))
                value_categories = ValueCategory.objects.filter(organisation=selected_org).annotate(lead_count=Count('leads'))
                filter_title = f"Categories for Organization: {selected_org.user.username}"
                
            else:
                # Show all categories aggregated
                source_categories = SourceCategory.objects.values('name').annotate(
                    lead_count=Count('leads')
                ).order_by('name')
                value_categories = ValueCategory.objects.values('name').annotate(
                    lead_count=Count('leads')
                ).order_by('name')
                filter_title = "All Categories (Aggregated)"
            
            context.update({
                "is_admin_view": True,
                "all_organizations": all_organizations,
                "agents": agents,
                "selected_org": selected_org,
                "selected_agent": selected_agent,
                "source_categories": source_categories,
                "value_categories": value_categories,
                "filter_title": filter_title,
            })
        else:
            # For organisor/agent: show only their categories
            if user.is_organisor:
                organisation = user.userprofile
            else:
                organisation = user.agent.organisation
                
            source_categories = SourceCategory.objects.filter(organisation=organisation).annotate(lead_count=Count('leads'))
            value_categories = ValueCategory.objects.filter(organisation=organisation).annotate(lead_count=Count('leads'))
            
            context.update({
                "is_admin_view": False,
                "source_categories": source_categories,
                "value_categories": value_categories,
            })

        return context

    def get_queryset(self):
        # Return empty queryset since we're not using old categories anymore
        return Category.objects.none()








class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/category_detail.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        leads = category.leads.all()
        context.update({
            "leads": leads
        })
        return context

    def get_queryset(self):
        user = self.request.user
        # Admin can see all categories
        if user.is_superuser or user.id == 1 or user.username == 'berk':
            queryset = Category.objects.all()
        elif user.is_organisor:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
        return queryset





class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
	template_name = "leads/lead_category_update.html"
	form_class = LeadCategoryUpdateForm

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['request'] = self.request
		return kwargs

	def get_queryset(self):
		user = self.request.user

		# Admin can see all leads
		if user.is_superuser:
			queryset = Lead.objects.all()
		elif user.is_organisor:
			queryset = Lead.objects.filter(organisation=user.userprofile)
		else:
			queryset = Lead.objects.filter(organisation=user.agent.organisation)
			queryset = queryset.filter(agent__user=user)
		return queryset
	
	def get_success_url(self):
		lead = self.get_object()
		if lead.category and lead.category.id == 0:  # Assuming 0 is the ID for "Unassigned" category
			return reverse("leads:category-detail", kwargs={"pk": 0})
		return reverse("leads:lead-detail", kwargs={"pk": lead.id})


def get_agents_by_org(request, org_id):
	"""AJAX endpoint to get agents, source categories and value categories by organization"""
	if not request.user.is_superuser:
		return JsonResponse({'error': 'Unauthorized'}, status=403)
	
	try:
		organisation = UserProfile.objects.get(id=org_id, user__is_organisor=True, user__is_superuser=False)
		
		# Agents - email'e göre sırala ve email'i göster
		agents = Agent.objects.filter(organisation=organisation).order_by('user__email')
		agents_data = [{'id': agent.id, 'name': f"{agent.user.email} ({agent.user.get_full_name() or agent.user.username})"} for agent in agents]
		
		# Source Categories
		source_categories = SourceCategory.objects.filter(organisation=organisation)
		source_categories_data = [{'id': cat.id, 'name': cat.name} for cat in source_categories]
		
		# Value Categories
		value_categories = ValueCategory.objects.filter(organisation=organisation)
		value_categories_data = [{'id': cat.id, 'name': cat.name} for cat in value_categories]
		
		return JsonResponse({
			'agents': agents_data,
			'source_categories': source_categories_data,
			'value_categories': value_categories_data
		})
		
	except UserProfile.DoesNotExist:
		return JsonResponse({'error': 'Organisation not found'}, status=404)
	except Exception as e:
		return JsonResponse({'error': str(e)}, status=500)