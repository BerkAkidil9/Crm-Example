from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.db.models import Q

from .models import ActivityLog
from leads.models import UserProfile, Agent

User = get_user_model()


class ActivityLogListView(LoginRequiredMixin, generic.ListView):
    """List of actions performed by the user. Admin can see all records."""
    model = ActivityLog
    template_name = "activity_log/activity_log_list.html"
    context_object_name = "activity_logs"
    paginate_by = 30

    def get_queryset(self):
        qs = ActivityLog.objects.select_related(
            "user", "organisation", "organisation__user", "affected_agent", "affected_agent__user"
        ).order_by("-created_at")
        if self.request.user.is_superuser:
            # Admin: optional user or organisation filter
            user_id = self.request.GET.get("user")
            org_id = self.request.GET.get("organisation")
            if user_id:
                qs = qs.filter(user_id=user_id)
            if org_id:
                qs = qs.filter(organisation_id=org_id)
            return qs
        if self.request.user.is_organisor:
            # Organisor: own actions + all activities in their organisation
            org = getattr(self.request.user, "userprofile", None)
            if org:
                qs = qs.filter(Q(user=self.request.user) | Q(organisation=org))
            else:
                qs = qs.filter(user=self.request.user)
            return qs
        # Agent: own actions + activities that affect them (lead/task assigned to them, order for their lead)
        agent_obj = Agent.objects.filter(user=self.request.user).first()
        if agent_obj:
            qs = qs.filter(Q(user=self.request.user) | Q(affected_agent=agent_obj))
        else:
            qs = qs.filter(user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context["filter_users"] = User.objects.filter(is_active=True).order_by("username")[:100]
            context["filter_organisations"] = UserProfile.objects.filter(
                user__is_organisor=True, user__is_superuser=False
            ).select_related("user").order_by("user__username")
            context["selected_user_id"] = self.request.GET.get("user", "")
            context["selected_organisation_id"] = self.request.GET.get("organisation", "")
        return context
