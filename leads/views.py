from typing import Any
from django.core.mail import send_mail
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.views import generic
from django.contrib import messages
from django.conf import settings
from agents.mixins import OrganisorAndLoginRequiredMixin
from .models import Lead, Agent, Category, UserProfile, EmailVerificationToken
from .forms import LeadForm, LeadModelForm, CustomUserCreationForm, AssignAgentForm, LeadCategoryUpdateForm, CustomAuthenticationForm





class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'
    
    def form_invalid(self, form):
        # Doğrulanmamış hesap için özel mesaj
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
        user.is_agent = True  # Set the user as an agent
        user.email_verified = False  # Email doğrulanmamış olarak başlat
        user.save()

        # Create UserProfile and Agent
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        Agent.objects.create(user=user, organisation=user_profile)

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

		if user.is_organisor:
			queryset = Lead.objects.filter(organisation=user.userprofile, agent__isnull=False)
		else:
			queryset = Lead.objects.filter(organisation=user.agent.organisation, agent__isnull=False)
			queryset = queryset.filter(agent__user=user)
		return queryset
	
	def get_context_data(self, **kwargs):
		context = super(LeadListView, self).get_context_data(**kwargs)
		user = self.request.user

		if user.is_organisor:
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

		if user.is_organisor:
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
	form_class = LeadModelForm

	def get_success_url(self):
		return reverse("leads:lead-list")
	
	def form_valid(self, form):
		lead = form.save(commit=False)
		lead.organisation = self.request.user.userprofile
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
	form_class = LeadModelForm

	def get_queryset(self):
		user = self.request.user
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

        # Get the unassigned category for displaying the count
        if user.is_organisor:
            unassigned_category = Category.objects.filter(name="Unassigned", organisation=user.userprofile).first()
        else:
            unassigned_category = Category.objects.filter(name="Unassigned", organisation=user.agent.organisation).first()

        context.update({
            "unassigned_category": unassigned_category
        })

        return context

    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            queryset = Category.objects.filter(organisation=user.userprofile).annotate(
                lead_count=Count('leads')
            )
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation).annotate(
                lead_count=Count('leads')
            )
        return queryset








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
        if user.is_organisor:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
        return queryset





class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
	template_name = "leads/lead_category_update.html"
	form_class = LeadCategoryUpdateForm

	def get_queryset(self):
		user = self.request.user

		if user.is_organisor:
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