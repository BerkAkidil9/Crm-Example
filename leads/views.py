from typing import Any
from django.core.mail import send_mail
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.http import HttpResponse, JsonResponse
from django.views import generic
from django.contrib import messages
from django.conf import settings
from django.db import models
from django.db.models import Q
from agents.mixins import OrganisorAndLoginRequiredMixin
from .models import Lead, Agent, Category, UserProfile, EmailVerificationToken, SourceCategory, ValueCategory
from .forms import LeadForm, LeadModelForm, CustomUserCreationForm, AssignAgentForm, LeadCategoryUpdateForm, CustomAuthenticationForm, AdminLeadModelForm, OrganisorLeadModelForm, CustomPasswordResetForm, CustomSetPasswordForm





class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        # Show specific message if email is not verified
        error_reason = self.request.session.pop('login_error_reason', None)
        if error_reason == 'email_not_verified':
            form._errors = {'__all__': form.error_class([
                "Please verify your email by clicking the verification link sent to your email address."
            ])}
        return super().form_invalid(form)

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/password_reset_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Redirect authenticated users to landing page
        if request.user.is_authenticated:
            return redirect('landing-page')
        return super().dispatch(request, *args, **kwargs)

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'registration/password_reset_confirm.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.user
        subject = 'Darkenyas CRM - Password Reset Successful'
        message = f"""Hello {user.first_name or user.username},

Your password has been successfully reset.

You can now login with your new password at: http://127.0.0.1:8000/login/

If you did not perform this action, please contact support immediately.

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
        return response
    
    def form_invalid(self, form):
        # Only show errors on actual form submission
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
            
            # Only show error message when both username and password are filled
            if username and form.cleaned_data.get('password', ''):
                messages.error(self.request, "Invalid username/email or password.")
        
        return super().form_invalid(form)

class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm

    def dispatch(self, request, *args, **kwargs):
        # Redirect authenticated users to landing page
        if request.user.is_authenticated:
            return redirect('landing-page')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("verify-email-sent")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.email = form.cleaned_data.get('email')
        user.first_name = form.cleaned_data.get('first_name')
        user.last_name = form.cleaned_data.get('last_name')
        user.is_organisor = True  # Set the user as an organisor (company owner)
        user.is_agent = False
        user.email_verified = False  # Start with email unverified
        user.save()

        # Create UserProfile and Organisor
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        from organisors.models import Organisor
        Organisor.objects.create(user=user, organisation=user_profile)

        # Create email verification token
        verification_token = EmailVerificationToken.objects.create(user=user)
        
        # Send verification email
        self.send_verification_email(user, verification_token.token)

        return super().form_valid(form)
    
    def send_verification_email(self, user, token):
        subject = 'Darkenyas CRM - Email Verification'
        message = f"""
        Hello {user.first_name},
        
        Welcome to Darkenyas CRM! Please click the link below to activate your account:
        
        http://127.0.0.1:8000/verify-email/{token}/
        
        This link is valid for 24 hours.
        
        If you didn't perform this action, you can ignore this email.
        
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
            
            return redirect('verify-email-success')
            
        except EmailVerificationToken.DoesNotExist:
            messages.error(request, "Invalid verification link.")
            return redirect('verify-email-failed')


class EmailVerificationSuccessView(generic.TemplateView):
    template_name = "registration/verify_email_success.html"


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
			queryset = Lead.objects.filter(agent__isnull=False).select_related("organisation", "agent", "source_category", "value_category")
		elif user.is_organisor:
			queryset = Lead.objects.filter(organisation=user.userprofile, agent__isnull=False).select_related("organisation", "agent", "source_category", "value_category")
		else:
			queryset = Lead.objects.filter(organisation=user.agent.organisation, agent__isnull=False).select_related("organisation", "agent", "source_category", "value_category")
			queryset = queryset.filter(agent__user=user)

		# Search (all roles)
		search = (self.request.GET.get("q") or "").strip()
		if search:
			queryset = queryset.filter(
				Q(first_name__icontains=search) |
				Q(last_name__icontains=search) |
				Q(email__icontains=search) |
				Q(phone_number__icontains=search)
			)

		# Admin-only filters
		if user.is_superuser:
			org_id = self.request.GET.get("organisation")
			if org_id:
				queryset = queryset.filter(organisation_id=org_id)
			agent_id = self.request.GET.get("agent")
			if agent_id:
				queryset = queryset.filter(agent_id=agent_id)
		# Organisor: filter by own agents
		elif user.is_organisor:
			agent_id = self.request.GET.get("agent")
			if agent_id:
				queryset = queryset.filter(agent_id=agent_id, agent__organisation=user.userprofile)

		return queryset

	def get_context_data(self, **kwargs):
		context = super(LeadListView, self).get_context_data(**kwargs)
		user = self.request.user

		# Unassigned leads (with same search and admin filters)
		if user.is_superuser:
			unassigned = Lead.objects.filter(agent__isnull=True)
		elif user.is_organisor:
			unassigned = Lead.objects.filter(organisation=user.userprofile, agent__isnull=True)
		else:
			unassigned = Lead.objects.none()

		search = (self.request.GET.get("q") or "").strip()
		if search:
			unassigned = unassigned.filter(
				Q(first_name__icontains=search) |
				Q(last_name__icontains=search) |
				Q(email__icontains=search) |
				Q(phone_number__icontains=search)
			)
		if user.is_superuser:
			org_id = self.request.GET.get("organisation")
			if org_id:
				unassigned = unassigned.filter(organisation_id=org_id)
			agent_id = self.request.GET.get("agent")
			if agent_id:
				unassigned = unassigned.filter(agent_id=agent_id)

		context["unassigned_leads"] = unassigned

		# Filter options for admin (always pass all agents so JS can filter by org without reload)
		if user.is_superuser:
			context["filter_organisations"] = UserProfile.objects.filter(user__is_organisor=True, user__is_superuser=False).order_by("user__username")
			context["filter_agents"] = Agent.objects.all().select_related("user", "organisation").order_by("user__username")
			org_id = self.request.GET.get("organisation") or ""
			agent_id = self.request.GET.get("agent") or ""
			if org_id and agent_id and not Agent.objects.filter(pk=agent_id, organisation_id=org_id).exists():
				agent_id = ""
			context["current_organisation_id"] = org_id
			context["current_agent_id"] = agent_id
		# Organisor: filter by own organisation's agents
		elif user.is_organisor:
			context["filter_agents"] = Agent.objects.filter(organisation=user.userprofile).select_related("user", "organisation").order_by("user__username")
			context["current_agent_id"] = self.request.GET.get("agent") or ""
		context["search_query"] = self.request.GET.get("q") or ""

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
		if user.is_superuser:
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
		if user.is_organisor:
			return OrganisorLeadModelForm
		return LeadModelForm

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['request'] = self.request
		return kwargs

	def get_initial(self):
		initial = super().get_initial()
		if self.request.user.is_superuser and self.request.method != 'POST':
			first_org = UserProfile.objects.filter(
				user__is_organisor=True,
				user__is_superuser=False
			).order_by('user__username').first()
			if first_org:
				initial['organisation'] = first_org.pk
		return initial

	def get_success_url(self):
		return reverse("leads:lead-list")
	
	def form_valid(self, form):
		lead = form.save(commit=False)
		user = self.request.user
		
		if user.is_superuser:
			# Use organisation selected in form (admin flow)
			if hasattr(form, 'cleaned_data') and 'organisation' in form.cleaned_data:
				lead.organisation = form.cleaned_data['organisation']
			else:
				# Fallback - use first organisation
				from leads.models import UserProfile
				default_org = UserProfile.objects.filter(user__is_organisor=True, user__is_superuser=False).first()
				if default_org:
					lead.organisation = default_org
		else:
			# Organisors use their own organisation
			lead.organisation = user.userprofile
			
		lead.save()
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
		if user.is_organisor:
			return OrganisorLeadModelForm
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
		if user.is_superuser:
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
        if user.is_superuser:
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
                ).order_by('name')
                value_categories = ValueCategory.objects.filter(
                    organisation=selected_agent.organisation
                ).annotate(
                    lead_count=Count('leads', filter=models.Q(leads__agent=selected_agent))
                ).order_by('name')
                filter_title = f"Categories for Agent: {selected_agent.user.username} ({selected_agent.organisation.user.username})"
                source_categories_with_leads = [
                    {"category": cat, "leads": list(Lead.objects.filter(source_category=cat, agent=selected_agent).select_related("agent"))}
                    for cat in source_categories
                ]
                value_categories_with_leads = [
                    {"category": cat, "leads": list(Lead.objects.filter(value_category=cat, agent=selected_agent).select_related("agent"))}
                    for cat in value_categories
                ]
                
            elif selected_org:
                # Show categories for specific organization
                source_categories = SourceCategory.objects.filter(organisation=selected_org).annotate(lead_count=Count('leads')).order_by('name')
                value_categories = ValueCategory.objects.filter(organisation=selected_org).annotate(lead_count=Count('leads')).order_by('name')
                filter_title = f"Categories for Organization: {selected_org.user.username}"
                source_categories_with_leads = [
                    {"category": cat, "leads": list(Lead.objects.filter(source_category=cat).select_related("agent"))}
                    for cat in source_categories
                ]
                value_categories_with_leads = [
                    {"category": cat, "leads": list(Lead.objects.filter(value_category=cat).select_related("agent"))}
                    for cat in value_categories
                ]
                
            else:
                # Show all categories aggregated; still provide lead list per category name
                source_categories = SourceCategory.objects.values('name').annotate(
                    lead_count=Count('leads')
                ).order_by('name')
                value_categories = ValueCategory.objects.values('name').annotate(
                    lead_count=Count('leads')
                ).order_by('name')
                filter_title = "All Categories (Aggregated)"
                source_categories_with_leads = [
                    {"category": {"name": s["name"], "lead_count": s["lead_count"]}, "leads": list(Lead.objects.filter(source_category__name=s["name"]).select_related("agent", "organisation"))}
                    for s in source_categories
                ]
                value_categories_with_leads = [
                    {"category": {"name": v["name"], "lead_count": v["lead_count"]}, "leads": list(Lead.objects.filter(value_category__name=v["name"]).select_related("agent", "organisation"))}
                    for v in value_categories
                ]
            
            context.update({
                "is_admin_view": True,
                "all_organizations": all_organizations,
                "agents": agents,
                "selected_org": selected_org,
                "selected_agent": selected_agent,
                "source_categories": source_categories,
                "value_categories": value_categories,
                "source_categories_with_leads": source_categories_with_leads,
                "value_categories_with_leads": value_categories_with_leads,
                "filter_title": filter_title,
            })
        else:
            # For organisor/agent: show only their categories, with optional agent filter and leads per category
            if user.is_organisor:
                organisation = user.userprofile
                filter_agents = Agent.objects.filter(organisation=organisation).select_related("user", "organisation").order_by("user__username")
                selected_agent_id = self.request.GET.get('agent')
                selected_agent = None
                if selected_agent_id:
                    try:
                        selected_agent = Agent.objects.filter(pk=selected_agent_id, organisation=organisation).select_related("user").first()
                    except (ValueError, Agent.DoesNotExist):
                        pass
                if selected_agent:
                    source_categories = SourceCategory.objects.filter(organisation=organisation).annotate(
                        lead_count=Count('leads', filter=models.Q(leads__agent=selected_agent))
                    ).order_by('name')
                    value_categories = ValueCategory.objects.filter(organisation=organisation).annotate(
                        lead_count=Count('leads', filter=models.Q(leads__agent=selected_agent))
                    ).order_by('name')
                    source_categories_with_leads = [
                        {"category": cat, "leads": list(Lead.objects.filter(source_category=cat, agent=selected_agent).select_related("agent"))}
                        for cat in source_categories
                    ]
                    value_categories_with_leads = [
                        {"category": cat, "leads": list(Lead.objects.filter(value_category=cat, agent=selected_agent).select_related("agent"))}
                        for cat in value_categories
                    ]
                else:
                    source_categories = SourceCategory.objects.filter(organisation=organisation).annotate(lead_count=Count('leads')).order_by('name')
                    value_categories = ValueCategory.objects.filter(organisation=organisation).annotate(lead_count=Count('leads')).order_by('name')
                    source_categories_with_leads = [
                        {"category": cat, "leads": list(Lead.objects.filter(source_category=cat).select_related("agent"))}
                        for cat in source_categories
                    ]
                    value_categories_with_leads = [
                        {"category": cat, "leads": list(Lead.objects.filter(value_category=cat).select_related("agent"))}
                        for cat in value_categories
                    ]
                context.update({
                    "is_admin_view": False,
                    "is_organisor_view": True,
                    "filter_agents": filter_agents,
                    "selected_agent": selected_agent,
                    "source_categories": source_categories,
                    "value_categories": value_categories,
                    "source_categories_with_leads": source_categories_with_leads,
                    "value_categories_with_leads": value_categories_with_leads,
                })
            else:
                organisation = user.agent.organisation
                source_categories = SourceCategory.objects.filter(organisation=organisation).annotate(lead_count=Count('leads')).order_by('name')
                value_categories = ValueCategory.objects.filter(organisation=organisation).annotate(lead_count=Count('leads')).order_by('name')
                source_categories_with_leads = [
                    {"category": cat, "leads": list(Lead.objects.filter(source_category=cat, agent=user.agent).select_related("agent"))}
                    for cat in source_categories
                ]
                value_categories_with_leads = [
                    {"category": cat, "leads": list(Lead.objects.filter(value_category=cat, agent=user.agent).select_related("agent"))}
                    for cat in value_categories
                ]
                context.update({
                    "is_admin_view": False,
                    "is_organisor_view": False,
                    "source_categories": source_categories,
                    "value_categories": value_categories,
                    "source_categories_with_leads": source_categories_with_leads,
                    "value_categories_with_leads": value_categories_with_leads,
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
        if user.is_superuser:
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
	if not request.user.is_authenticated:
		return JsonResponse({'error': 'Unauthorized'}, status=403)
	try:
		# Organisation dropdown only lists organisors, so this is always an organisor org
		organisation = UserProfile.objects.get(id=org_id, user__is_organisor=True, user__is_superuser=False)
		# Seçilen org için varsayılan kategoriler yoksa oluştur (org 2, 3... seçildiğinde de dolu gelsin)
		_default_source = [
			"Website", "Social Media", "Email Campaign", "Cold Call", "Referral",
			"Trade Show", "Advertisement", "Direct Mail", "SEO/Google", "Unassigned"
		]
		_default_value = [
			"Enterprise", "SMB", "Small Business", "Individual",
			"High Value", "Medium Value", "Low Value", "Unassigned"
		]
		for name in _default_source:
			SourceCategory.objects.get_or_create(name=name, organisation=organisation)
		for name in _default_value:
			ValueCategory.objects.get_or_create(name=name, organisation=organisation)
		# Agents - isim soyisim (email) formatında
		agents = Agent.objects.filter(organisation=organisation).select_related('user').order_by('user__email')
		agents_data = [
			{'id': agent.id, 'name': f"{agent.user.get_full_name() or agent.user.username} ({agent.user.email})"}
			for agent in agents
		]
		
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