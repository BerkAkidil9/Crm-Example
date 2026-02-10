"""
Tests for tasks.forms – TaskForm, TaskFormAdmin, TaskFormWithAssignee.
"""
from datetime import date, timedelta

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model

from tasks.forms import TaskForm, TaskFormAdmin, TaskFormWithAssignee
from leads.models import UserProfile, Agent

User = get_user_model()


class TaskFormTestBase(TestCase):
    """Shared setUp for task form tests."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            username='formadmin', email='formadmin@test.com', password='testpass123',
        )
        cls.organisor_user = User.objects.create_user(
            username='formorg', email='formorg@test.com', password='testpass123',
            is_organisor=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.organisor_user)
        cls.agent_user = User.objects.create_user(
            username='formagent', email='formagent@test.com', password='testpass123',
            is_agent=True,
        )
        cls.agent = Agent.objects.create(user=cls.agent_user, organisation=cls.organisation)
        cls.factory = RequestFactory()


# ---------------------------------------------------------------------------
# TaskForm (agent self-assign form)
# ---------------------------------------------------------------------------
class TestTaskForm(TaskFormTestBase):

    def get_valid_data(self):
        return {
            'title': 'Test Task',
            'content': 'Description',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=5)).isoformat(),
            'status': 'pending',
            'priority': 'medium',
        }

    def test_valid_data(self):
        form = TaskForm(data=self.get_valid_data(), request=None, organisation=None)
        self.assertTrue(form.is_valid())

    def test_required_fields(self):
        form = TaskForm(data={}, request=None, organisation=None)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('start_date', form.errors)
        self.assertIn('end_date', form.errors)

    def test_content_not_required(self):
        data = self.get_valid_data()
        data['content'] = ''
        form = TaskForm(data=data, request=None, organisation=None)
        self.assertTrue(form.is_valid())

    def test_end_date_before_start_date(self):
        data = self.get_valid_data()
        data['start_date'] = (date.today() + timedelta(days=5)).isoformat()
        data['end_date'] = date.today().isoformat()
        form = TaskForm(data=data, request=None, organisation=None)
        self.assertFalse(form.is_valid())
        self.assertIn('End date cannot be before start date', str(form.errors))

    def test_same_start_and_end_date(self):
        data = self.get_valid_data()
        data['start_date'] = date.today().isoformat()
        data['end_date'] = date.today().isoformat()
        form = TaskForm(data=data, request=None, organisation=None)
        self.assertTrue(form.is_valid())

    def test_status_choices(self):
        for status_val, _ in [('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')]:
            data = self.get_valid_data()
            data['status'] = status_val
            form = TaskForm(data=data, request=None, organisation=None)
            self.assertTrue(form.is_valid(), f'Status {status_val} should be valid')

    def test_priority_choices(self):
        for p_val, _ in [('critical', ''), ('high', ''), ('medium', ''), ('low', '')]:
            data = self.get_valid_data()
            data['priority'] = p_val
            form = TaskForm(data=data, request=None, organisation=None)
            self.assertTrue(form.is_valid(), f'Priority {p_val} should be valid')

    def test_invalid_status(self):
        data = self.get_valid_data()
        data['status'] = 'invalid_status'
        form = TaskForm(data=data, request=None, organisation=None)
        self.assertFalse(form.is_valid())

    def test_invalid_priority(self):
        data = self.get_valid_data()
        data['priority'] = 'invalid_priority'
        form = TaskForm(data=data, request=None, organisation=None)
        self.assertFalse(form.is_valid())

    def test_fields_in_meta(self):
        form = TaskForm(request=None, organisation=None)
        expected = {'title', 'content', 'start_date', 'end_date', 'status', 'priority'}
        self.assertEqual(set(form.Meta.fields), expected)

    def test_widgets_have_css_classes(self):
        form = TaskForm(request=None, organisation=None)
        for field_name in ['title', 'content', 'start_date', 'end_date', 'status', 'priority']:
            widget = form.fields[field_name].widget
            self.assertIn('class', widget.attrs)


# ---------------------------------------------------------------------------
# TaskFormWithAssignee (organisor form)
# ---------------------------------------------------------------------------
class TestTaskFormWithAssignee(TaskFormTestBase):

    def get_valid_data(self):
        return {
            'title': 'Org Task',
            'content': 'Details',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=3)).isoformat(),
            'status': 'pending',
            'priority': 'high',
            'assigned_to': self.agent_user.pk,
        }

    def test_valid_data(self):
        form = TaskFormWithAssignee(
            data=self.get_valid_data(),
            request=None,
            organisation=self.organisation,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_assigned_to_field_present(self):
        form = TaskFormWithAssignee(request=None, organisation=self.organisation)
        self.assertIn('assigned_to', form.fields)

    def test_assigned_to_queryset_filtered_by_org(self):
        form = TaskFormWithAssignee(request=None, organisation=self.organisation)
        qs = form.fields['assigned_to'].queryset
        user_ids = list(qs.values_list('pk', flat=True))
        self.assertIn(self.agent_user.pk, user_ids)

    def test_assigned_to_required(self):
        data = self.get_valid_data()
        del data['assigned_to']
        form = TaskFormWithAssignee(
            data=data, request=None, organisation=self.organisation,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('assigned_to', form.errors)

    def test_end_date_validation(self):
        data = self.get_valid_data()
        data['start_date'] = (date.today() + timedelta(days=10)).isoformat()
        data['end_date'] = date.today().isoformat()
        form = TaskFormWithAssignee(
            data=data, request=None, organisation=self.organisation,
        )
        self.assertFalse(form.is_valid())

    def test_fields_include_assigned_to(self):
        self.assertIn('assigned_to', TaskFormWithAssignee.Meta.fields)


# ---------------------------------------------------------------------------
# TaskFormAdmin (superuser form)
# ---------------------------------------------------------------------------
class TestTaskFormAdmin(TaskFormTestBase):

    def test_organisation_queryset(self):
        request = self.factory.get('/')
        request.user = self.admin
        form = TaskFormAdmin(request=request, exclude_user_pk=self.admin.pk, organisation=None)
        org_qs = form.fields['organisation'].queryset
        # Should include organisor but not superuser
        self.assertIn(self.organisation, org_qs)

    def test_assigned_to_pk_choices_with_org(self):
        request = self.factory.get('/')
        request.user = self.admin
        form = TaskFormAdmin(
            request=request, exclude_user_pk=self.admin.pk,
            organisation=self.organisation,
        )
        choices = form.fields['assigned_to_pk'].choices
        pks = [c[0] for c in choices]
        self.assertIn(str(self.agent_user.pk), pks)

    def test_assigned_to_pk_empty_without_org(self):
        request = self.factory.get('/')
        request.user = self.admin
        form = TaskFormAdmin(request=request, exclude_user_pk=self.admin.pk, organisation=None)
        choices = form.fields['assigned_to_pk'].choices
        self.assertEqual(len(choices), 0)

    def test_clean_assigned_to_pk_self_assign_rejected(self):
        request = self.factory.get('/')
        request.user = self.admin
        data = {
            'organisation': self.organisation.pk,
            'title': 'Admin Task',
            'content': '',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=1)).isoformat(),
            'status': 'pending',
            'priority': 'medium',
            'assigned_to_pk': str(self.admin.pk),
        }
        form = TaskFormAdmin(
            data=data, request=request,
            exclude_user_pk=self.admin.pk,
            organisation=self.organisation,
        )
        # Admin's pk should NOT be in the choices, so the form should be invalid
        self.assertFalse(form.is_valid())

    def test_end_date_before_start_date(self):
        request = self.factory.get('/')
        request.user = self.admin
        data = {
            'organisation': self.organisation.pk,
            'title': 'Date Fail',
            'content': '',
            'start_date': (date.today() + timedelta(days=5)).isoformat(),
            'end_date': date.today().isoformat(),
            'status': 'pending',
            'priority': 'medium',
            'assigned_to_pk': str(self.agent_user.pk),
        }
        form = TaskFormAdmin(
            data=data, request=request,
            exclude_user_pk=self.admin.pk,
            organisation=self.organisation,
        )
        self.assertFalse(form.is_valid())

    def test_organisation_field_present(self):
        request = self.factory.get('/')
        request.user = self.admin
        form = TaskFormAdmin(request=request, exclude_user_pk=self.admin.pk, organisation=None)
        self.assertIn('organisation', form.fields)
        self.assertIn('assigned_to_pk', form.fields)
