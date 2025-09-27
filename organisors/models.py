from django.db import models
from leads.models import User, UserProfile

class Organisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = "Organisor"
        verbose_name_plural = "Organisors"