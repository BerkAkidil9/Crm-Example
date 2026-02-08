from django import forms
from django.contrib.auth import get_user_model
from .models import Task
from leads.models import Agent, UserProfile

User = get_user_model()


class OrganisationChoiceField(forms.ModelChoiceField):
    """Display organisation as username (email)."""

    def label_from_instance(self, obj):
        return f"{obj.user.username} ({obj.user.email})"


class UserChoiceField(forms.ModelChoiceField):
    """Display user as username (email)."""

    def label_from_instance(self, obj):
        return f"{obj.username} ({obj.email})"


class TaskForm(forms.ModelForm):
    """Task create/update form (agent: self-assign only)."""

    class Meta:
        model = Task
        fields = ['title', 'content', 'start_date', 'end_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500', 'placeholder': 'Task title'}),
            'content': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500', 'rows': 4, 'placeholder': 'Task description'}),
            'start_date': forms.DateInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.organisation = kwargs.pop('organisation', None)
        kwargs.pop('exclude_user_pk', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        data = super().clean()
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end and end < start:
            raise forms.ValidationError('End date cannot be before start date.')
        return data


class TaskFormAdmin(forms.ModelForm):
    """Admin: select organisation first, then assign to an agent. Current user (admin) is never in the list."""

    organisation = OrganisationChoiceField(
        queryset=UserProfile.objects.none(),
        required=True,
        label='Organisation',
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'}),
    )
    assigned_to_pk = forms.ChoiceField(
        required=True,
        label='Assign to Agent',
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'}),
    )

    class Meta:
        model = Task
        fields = ['organisation', 'title', 'content', 'start_date', 'end_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500', 'placeholder': 'Task title'}),
            'content': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500', 'rows': 4, 'placeholder': 'Task description'}),
            'start_date': forms.DateInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        exclude_user_pk = kwargs.pop('exclude_user_pk', None)
        if exclude_user_pk is not None:
            exclude_user_pk = int(exclude_user_pk)
        self._exclude_user_pk = exclude_user_pk
        data = kwargs.get('data')
        organisation = kwargs.pop('organisation', None)
        super().__init__(*args, **kwargs)
        org = organisation
        if org is None and data:
            org_id = data.get('organisation')
            if org_id:
                try:
                    org = UserProfile.objects.get(pk=org_id)
                except UserProfile.DoesNotExist:
                    pass
        if org is None and self.instance and self.instance.pk:
            org = self.instance.organisation

        # Organisation list: organisors only, NEVER current user (admin) or any superuser
        org_qs = (
            UserProfile.objects.filter(user__is_organisor=True)
            .exclude(user__is_superuser=True)
            .order_by('user__username')
        )
        if self.request and self.request.user.is_authenticated:
            org_qs = org_qs.exclude(user=self.request.user)
        self.fields['organisation'].queryset = org_qs

        # Build choices: only agents of this org; NEVER superusers (admin) and NEVER current user
        if org:
            agents = (
                Agent.objects.filter(organisation=org)
                .exclude(user__is_superuser=True)
                .select_related('user')
                .order_by('user__username')
            )
            choices = []
            for agent in agents:
                uid = agent.user_id
                if exclude_user_pk is not None and uid == exclude_user_pk:
                    continue
                label = f"{agent.user.username} ({agent.user.email})"
                choices.append((str(uid), label))
            if self.instance and self.instance.pk and self.instance.assigned_to_id:
                aid = self.instance.assigned_to_id
                if not self.instance.assigned_to.is_superuser and aid != exclude_user_pk and not any(c[0] == str(aid) for c in choices):
                    choices.append((str(aid), f"{self.instance.assigned_to.username} ({self.instance.assigned_to.email})"))
            self.fields['assigned_to_pk'].choices = choices
        else:
            self.fields['assigned_to_pk'].choices = []

    def clean_assigned_to_pk(self):
        pk = self.cleaned_data.get('assigned_to_pk')
        if self._exclude_user_pk is not None and pk and int(pk) == self._exclude_user_pk:
            raise forms.ValidationError('You cannot assign tasks to yourself.')
        return pk

    def clean(self):
        data = super().clean()
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end and end < start:
            raise forms.ValidationError('End date cannot be before start date.')
        return data


class TaskFormWithAssignee(TaskForm):
    """Organisor: assign to one of their agents only (no organisor in list). Shows username (email)."""

    assigned_to = UserChoiceField(
        queryset=User.objects.none(),
        required=True,
        label='Assign to Agent',
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'}),
    )

    class Meta(TaskForm.Meta):
        fields = ['title', 'content', 'start_date', 'end_date', 'status', 'assigned_to']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.organisation:
            # Only agents of this organisation (exclude organisor)
            agent_user_ids = list(Agent.objects.filter(organisation=self.organisation).values_list('user_id', flat=True))
            if self.instance and self.instance.pk and self.instance.assigned_to_id:
                agent_user_ids = list(set(agent_user_ids) | {self.instance.assigned_to_id})
            self.fields['assigned_to'].queryset = User.objects.filter(pk__in=agent_user_ids).order_by('username')
