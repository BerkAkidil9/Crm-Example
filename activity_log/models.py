from django.db import models
from django.conf import settings
from django.urls import reverse


# Human-readable action constants
ACTION_ORGANISOR_CREATED = 'organisor_created'
ACTION_ORGANISOR_UPDATED = 'organisor_updated'
ACTION_ORGANISOR_DELETED = 'organisor_deleted'
ACTION_AGENT_CREATED = 'agent_created'
ACTION_AGENT_UPDATED = 'agent_updated'
ACTION_AGENT_DELETED = 'agent_deleted'
ACTION_PRODUCT_CREATED = 'product_created'
ACTION_PRODUCT_UPDATED = 'product_updated'
ACTION_PRODUCT_DELETED = 'product_deleted'
ACTION_PRICE_INCREASED = 'price_increased'
ACTION_PRICE_DECREASED = 'price_decreased'
ACTION_PRICE_BULK_UPDATE = 'price_bulk_update'
ACTION_ORDER_CREATED = 'order_created'
ACTION_ORDER_UPDATED = 'order_updated'
ACTION_ORDER_CANCELLED = 'order_cancelled'
ACTION_LEAD_CREATED = 'lead_created'
ACTION_LEAD_UPDATED = 'lead_updated'
ACTION_LEAD_DELETED = 'lead_deleted'
ACTION_TASK_CREATED = 'task_created'
ACTION_TASK_UPDATED = 'task_updated'
ACTION_TASK_DELETED = 'task_deleted'

ACTION_CHOICES = [
    (ACTION_ORGANISOR_CREATED, 'Organisor created'),
    (ACTION_ORGANISOR_UPDATED, 'Organisor updated'),
    (ACTION_ORGANISOR_DELETED, 'Organisor deleted'),
    (ACTION_AGENT_CREATED, 'Agent created'),
    (ACTION_AGENT_UPDATED, 'Agent updated'),
    (ACTION_AGENT_DELETED, 'Agent deleted'),
    (ACTION_PRODUCT_CREATED, 'Product created'),
    (ACTION_PRODUCT_UPDATED, 'Product updated'),
    (ACTION_PRODUCT_DELETED, 'Product deleted'),
    (ACTION_PRICE_INCREASED, 'Price increased'),
    (ACTION_PRICE_DECREASED, 'Price decreased'),
    (ACTION_PRICE_BULK_UPDATE, 'Bulk price update'),
    (ACTION_ORDER_CREATED, 'Order created'),
    (ACTION_ORDER_UPDATED, 'Order updated'),
    (ACTION_ORDER_CANCELLED, 'Order cancelled'),
    (ACTION_LEAD_CREATED, 'Lead created'),
    (ACTION_LEAD_UPDATED, 'Lead updated'),
    (ACTION_LEAD_DELETED, 'Lead deleted'),
    (ACTION_TASK_CREATED, 'Task created'),
    (ACTION_TASK_UPDATED, 'Task updated'),
    (ACTION_TASK_DELETED, 'Task deleted'),
]

OBJECT_TYPE_CHOICES = [
    ('organisor', 'Organisor'),
    ('agent', 'Agent'),
    ('product', 'Product / Stock'),
    ('order', 'Order'),
    ('lead', 'Lead'),
    ('task', 'Task'),
]


class ActivityLog(models.Model):
    """Log of meaningful actions performed by users (admin, organisor, agent)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='activity_logs',
        verbose_name='User'
    )
    action = models.CharField(
        max_length=32,
        choices=ACTION_CHOICES,
        verbose_name='Action'
    )
    object_type = models.CharField(
        max_length=20,
        choices=OBJECT_TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name='Object type'
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Object ID'
    )
    object_repr = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Object summary'
    )
    details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Details',
        help_text='E.g. old_price, new_price, product_name'
    )
    organisation = models.ForeignKey(
        'leads.UserProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs',
        verbose_name='Organisation'
    )
    affected_agent = models.ForeignKey(
        'leads.Agent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs_affecting',
        verbose_name='Affected agent',
        help_text='Agent who is affected by this action (e.g. lead/task assigned to them, order for their lead)'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Activity log entry'
        verbose_name_plural = 'Activity logs'

    def __str__(self):
        user_str = self.user.get_full_name() or self.user.username if self.user else 'Unknown'
        return f"{user_str} - {self.get_action_display()} ({self.created_at})"

    def get_detail_url(self):
        """Return URL to the related object's detail page, or None if not available."""
        if not self.object_type or self.object_id is None:
            return None
        url_config = {
            'order': ('orders', 'order-detail', {'pk': self.object_id}),
            'lead': ('leads', 'lead-detail', {'pk': self.object_id}),
            'task': ('tasks', 'task-detail', {'pk': self.object_id}),
            'product': ('ProductsAndStock', 'ProductAndStock-detail', {'pk': self.object_id}),
            'agent': ('agents', 'agent-detail', {'pk': self.object_id}),
            'organisor': ('organisors', 'organisor-detail', {'pk': self.object_id}),
        }
        if self.object_type not in url_config:
            return None
        namespace, name, kwargs = url_config[self.object_type]
        try:
            return reverse(f'{namespace}:{name}', kwargs=kwargs)
        except Exception:
            return None


def log_activity(user, action, object_type=None, object_id=None, object_repr='', details=None, organisation=None, affected_agent=None):
    """
    Create an activity log entry.
    - user: User who performed the action (request.user)
    - action: One of the ACTION_* constants
    - object_type: 'organisor', 'agent', 'product', 'order', 'lead', 'task'
    - object_id: Primary key of the related object
    - object_repr: Display text (e.g. "Product: Laptop", "Order: Ord-001")
    - details: dict, extra info (e.g. {"old_price": 100, "new_price": 120})
    - organisation: UserProfile (which organisation the action belongs to)
    - affected_agent: Agent instance when this action concerns a specific agent (e.g. lead/task assigned to them, order for their lead)
    """
    if not user or not user.is_authenticated:
        return None
    return ActivityLog.objects.create(
        user=user,
        action=action,
        object_type=object_type or '',
        object_id=object_id,
        object_repr=(object_repr or '')[:255],
        details=details or {},
        organisation=organisation,
        affected_agent=affected_agent,
    )
