from django.views import generic
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404

from agents.mixins import OrganisorAndLoginRequiredMixin
from leads.models import Agent, UserProfile
from .models import Task
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
        status = self.request.GET.get('status', '').strip()
        if status:
            qs = qs.filter(status=status)
        search = self.request.GET.get('q', '').strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(content__icontains=search))
        return qs.order_by('-created_at')


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
        if self.request.user.is_superuser:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            self.object.organisation = form.cleaned_data['organisation']
            self.object.assigned_to = User.objects.get(pk=int(form.cleaned_data['assigned_to_pk']))
            self.object.assigned_by = self.request.user
        elif self.request.user.is_organisor:
            self.object.assigned_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('tasks:task-detail', kwargs={'pk': self.object.pk})


class TaskDeleteView(TaskAccessMixin, generic.DeleteView):
    model = Task
    template_name = 'tasks/task_delete.html'
    context_object_name = 'task'

    def get_success_url(self):
        return reverse('tasks:task-list')
