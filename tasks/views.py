from django.views import generic
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic.base import View
from django.contrib import messages

from agents.mixins import OrganisorAndLoginRequiredMixin
from leads.models import Agent, UserProfile
from activity_log.models import log_activity, ACTION_TASK_CREATED, ACTION_TASK_UPDATED, ACTION_TASK_DELETED
from .models import Task, Notification
from .forms import TaskForm, TaskFormWithAssignee, TaskFormAdmin


class TaskAccessMixin(LoginRequiredMixin):
    """Task list/detail: organisor sees all org tasks, agent sees only tasks assigned to them."""

    def get_queryset(self):
        qs = Task.objects.select_related('assigned_to', 'assigned_by', 'organisation')
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.request.user.is_superuser:
            return qs.all()
        if self.request.user.is_organisor:
            org = self.request.user.userprofile
            return qs.filter(organisation=org)
        if self.request.user.is_agent:
            return qs.filter(assigned_to=self.request.user)
        return qs.none()


class TaskListView(TaskAccessMixin, generic.ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'task_list'
    paginate_by = 15

    def get_queryset(self):
        from django.db.models import Q
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            org_id = self.request.GET.get('organisation', '').strip()
            if org_id:
                qs = qs.filter(organisation_id=org_id)
            agent_id = self.request.GET.get('agent', '').strip()
            if agent_id:
                try:
                    agent_user_id = Agent.objects.filter(pk=agent_id).values_list('user_id', flat=True).first()
                    if agent_user_id:
                        qs = qs.filter(assigned_to_id=agent_user_id)
                except (ValueError, TypeError):
                    pass
        elif user.is_organisor:
            agent_id = self.request.GET.get('agent', '').strip()
            if agent_id:
                try:
                    agent = Agent.objects.filter(pk=agent_id, organisation=user.userprofile).first()
                    if agent:
                        qs = qs.filter(assigned_to_id=agent.user_id)
                except (ValueError, TypeError):
                    pass
        status = self.request.GET.get('status', '').strip()
        if status:
            qs = qs.filter(status=status)
        priority = self.request.GET.get('priority', '').strip()
        if priority:
            qs = qs.filter(priority=priority)
        search = self.request.GET.get('q', '').strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(content__icontains=search))
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_superuser or user.is_organisor:
            selected_org_id = self.request.GET.get("organisation", "")
            selected_agent_id = self.request.GET.get("agent", "")
            context["selected_organisation_id"] = selected_org_id
            context["selected_agent_id"] = selected_agent_id
            if user.is_superuser:
                org_qs = UserProfile.objects.filter(user__is_organisor=True).select_related("user").order_by("user__username")
                profile = getattr(user, "userprofile", None)
                if profile:
                    org_qs = org_qs.exclude(pk=profile.pk)
                context["organisations"] = org_qs
                context["show_organisation_filter"] = True
                if selected_org_id:
                    context["agents"] = Agent.objects.filter(organisation_id=selected_org_id).select_related("user").order_by("user__username")
                else:
                    context["agents"] = []
            else:
                context["organisations"] = []
                context["show_organisation_filter"] = False
                context["agents"] = Agent.objects.filter(organisation=user.userprofile).select_related("user").order_by("user__username")
        else:
            context["show_organisation_filter"] = False
            context["organisations"] = []
            context["agents"] = []
            context["selected_organisation_id"] = context["selected_agent_id"] = ""
        return context


class TaskDetailView(TaskAccessMixin, generic.DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    template_name = 'tasks/task_create.html'
    context_object_name = 'task'

    def get_form_class(self):
        if self.request.user.is_superuser:
            return TaskFormAdmin
        if self.request.user.is_organisor:
            return TaskFormWithAssignee
        return TaskForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['exclude_user_pk'] = self.request.user.pk if self.request.user.is_authenticated else None
        org = self._get_organisation()
        kwargs['organisation'] = org
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_superuser:
            org = self._get_organisation()
            if org:
                initial['organisation'] = org
        return initial

    def _get_organisation(self):
        if self.request.user.is_superuser:
            org_id = self.request.POST.get('organisation') or self.request.GET.get('organisation')
            if org_id:
                return get_object_or_404(UserProfile, pk=org_id)
            return None
        if self.request.user.is_organisor:
            return self.request.user.userprofile
        if self.request.user.is_agent:
            return Agent.objects.get(user=self.request.user).organisation
        return None

    def form_valid(self, form):
        task = form.save(commit=False)
        if self.request.user.is_superuser:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            task.organisation = form.cleaned_data['organisation']
            task.assigned_to = User.objects.get(pk=int(form.cleaned_data['assigned_to_pk']))
            task.assigned_by = self.request.user
        elif self.request.user.is_organisor:
            task.organisation = self._get_organisation()
            task.assigned_to = form.cleaned_data['assigned_to']
            task.assigned_by = self.request.user
        else:
            task.organisation = self._get_organisation()
            task.assigned_to = self.request.user
            task.assigned_by = None
        task.save()
        assigned_agent = Agent.objects.filter(user=task.assigned_to).first()
        log_activity(
            self.request.user,
            ACTION_TASK_CREATED,
            object_type='task',
            object_id=task.pk,
            object_repr=f"Task: {task.title}",
            organisation=task.organisation,
            affected_agent=assigned_agent,
        )
        # Notify assignee: new task assigned to you
        if task.assigned_to_id and task.assigned_to_id != self.request.user.pk:
            task_url = reverse('tasks:task-detail', kwargs={'pk': task.pk})
            Notification.objects.get_or_create(
                user_id=task.assigned_to_id,
                task=task,
                key=f"task_assigned_{task.id}",
                defaults={
                    'title': f'New task assigned to you: {task.title}',
                    'message': f'A new task "{task.title}" (due {task.end_date}) has been assigned to you.',
                    'action_url': task_url,
                    'action_label': 'View Task',
                },
            )
        messages.success(self.request, "Task created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('tasks:task-detail', kwargs={'pk': self.object.pk})


class TaskUpdateView(TaskAccessMixin, generic.UpdateView):
    model = Task
    template_name = 'tasks/task_update.html'
    context_object_name = 'task'

    def get_form_class(self):
        if self.request.user.is_superuser:
            return TaskFormAdmin
        if self.request.user.is_organisor:
            return TaskFormWithAssignee
        return TaskForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['exclude_user_pk'] = self.request.user.pk if self.request.user.is_authenticated else None
        kwargs['organisation'] = self.object.organisation
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_superuser and self.object.assigned_to_id:
            initial['assigned_to_pk'] = str(self.object.assigned_to_id)
        return initial

    def form_valid(self, form):
        previous_assigned_to_pk = self.object.assigned_to_id
        if self.request.user.is_superuser:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            self.object.organisation = form.cleaned_data['organisation']
            self.object.assigned_to = User.objects.get(pk=int(form.cleaned_data['assigned_to_pk']))
            self.object.assigned_by = self.request.user
        elif self.request.user.is_organisor:
            self.object.assigned_by = self.request.user
        response = super().form_valid(form)
        # Notify new assignee if assignee changed
        new_pk = self.object.assigned_to_id
        if new_pk and new_pk != previous_assigned_to_pk and new_pk != self.request.user.pk:
            task_url = reverse('tasks:task-detail', kwargs={'pk': self.object.pk})
            Notification.objects.create(
                user_id=new_pk,
                task=self.object,
                title=f'Task assigned to you: {self.object.title}',
                message=f'Task "{self.object.title}" (due {self.object.end_date}) has been assigned to you.',
                action_url=task_url,
                action_label='View Task',
            )
        assigned_agent = Agent.objects.filter(user=self.object.assigned_to).first()
        messages.success(self.request, "Task updated successfully.")
        log_activity(
            self.request.user,
            ACTION_TASK_UPDATED,
            object_type='task',
            object_id=self.object.pk,
            object_repr=f"Task: {self.object.title}",
            organisation=self.object.organisation,
            affected_agent=assigned_agent,
        )
        return response

    def get_success_url(self):
        return reverse('tasks:task-detail', kwargs={'pk': self.object.pk})


class TaskDeleteView(TaskAccessMixin, generic.DeleteView):
    model = Task
    template_name = 'tasks/task_delete.html'
    context_object_name = 'task'

    def get_success_url(self):
        return reverse('tasks:task-list')

    def form_valid(self, form):
        task = self.get_object()
        assigned_agent = Agent.objects.filter(user=task.assigned_to).first()
        log_activity(
            self.request.user,
            ACTION_TASK_DELETED,
            object_type='task',
            object_id=task.pk,
            object_repr=f"Task: {task.title}",
            organisation=task.organisation,
            affected_agent=assigned_agent,
        )
        messages.success(self.request, "Task deleted successfully.")
        return super().form_valid(form)


class NotificationListView(LoginRequiredMixin, generic.ListView):
    """List all notifications for the current user."""
    model = Notification
    template_name = 'tasks/notification_list.html'
    context_object_name = 'notification_list'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).select_related('task')


class NotificationMarkReadView(LoginRequiredMixin, View):
    """Mark a single notification as read and redirect to task or notification list."""

    def get(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        if notification.task_id:
            return redirect('tasks:task-detail', pk=notification.task_id)
        return redirect('tasks:notification-list')


class NotificationMarkAllReadView(LoginRequiredMixin, View):
    """Mark all notifications as read."""

    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return redirect('tasks:notification-list')

    def get(self, request):
        return redirect('tasks:notification-list')
