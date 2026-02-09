from django.db import models
from django.conf import settings
from django.urls import reverse


class Task(models.Model):
    """Task model: title, content, start/end date, assignee, assigned by."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    title = models.CharField(max_length=200, verbose_name='Title')
    content = models.TextField(blank=True, verbose_name='Content')
    start_date = models.DateField(verbose_name='Start Date')
    end_date = models.DateField(verbose_name='End Date')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status',
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='Priority',
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        verbose_name='Assigned To',
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_assigned_by',
        verbose_name='Assigned By',
    )
    organisation = models.ForeignKey(
        'leads.UserProfile',
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Organisation',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return self.title


class Notification(models.Model):
    """In-app notification for a user (e.g. task deadline reminder)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    # Unique key to avoid duplicate reminders (e.g. task_deadline_12_3d)
    key = models.CharField(max_length=120, unique=True, blank=True, null=True)
    # Shortcut: "View Task", "View Lead", "View Order", "View Product" etc.
    action_url = models.CharField(max_length=255, blank=True, null=True)
    action_label = models.CharField(max_length=80, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    @property
    def display_url(self):
        """URL for the 'View' shortcut; uses action_url or task detail fallback."""
        if self.action_url:
            return self.action_url
        if self.task_id:
            return reverse('tasks:task-detail', kwargs={'pk': self.task_id})
        return None

    @property
    def display_label(self):
        """Label for the 'View' shortcut."""
        if self.action_label:
            return self.action_label
        if self.task_id:
            return 'View Task'
        return None
