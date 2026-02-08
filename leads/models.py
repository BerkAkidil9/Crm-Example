from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from django.utils import timezone
from datetime import timedelta
from phonenumber_field.modelfields import PhoneNumberField

class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    is_organisor = models.BooleanField(default=True)
    is_agent = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_number = PhoneNumberField(blank=True, null=True, unique=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    profile_image = models.FileField(upload_to='profile_images/', blank=True, null=True, help_text="Upload a profile picture")
    
    # Email ve username unique olacak şekilde ayarla
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[AbstractUser.username_validator],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')

    def __str__(self):
        return self.user.username

    class Meta:
        unique_together = ('user',)  # Ensure a unique UserProfile per User

class Category(models.Model):
    name = models.CharField(max_length=30)
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class SourceCategory(models.Model):
    """Kaynak bazlı kategoriler - Müşteri adayının nereden geldiği"""
    name = models.CharField(max_length=50)
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Source Categories"

class ValueCategory(models.Model):
    """Değer bazlı kategoriler - Müşteri adayının potansiyel değeri"""
    name = models.CharField(max_length=50)
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Value Categories"

class Lead(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    age = models.IntegerField(default=0)
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    agent = models.ForeignKey("Agent", null=True, blank=True, on_delete=models.SET_NULL)
    category = models.ForeignKey("Category", related_name="leads", null=True, blank=True, on_delete=models.SET_NULL)
    source_category = models.ForeignKey("SourceCategory", related_name="leads", null=True, blank=True, on_delete=models.SET_NULL)
    value_category = models.ForeignKey("ValueCategory", related_name="leads", null=True, blank=True, on_delete=models.SET_NULL)
    description = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=255)
    profile_image = models.FileField(upload_to='lead_photos/', blank=True, null=True, help_text="Lead profile photo")

    def save(self, *args, **kwargs):
        # Sadece yeni lead oluştururken kategorileri ata (pk yoksa)
        is_new = self.pk is None
        
        if is_new:
            # Eski category sistemi için backward compatibility
            if not self.category:
                try:
                    unassigned_category = Category.objects.get(name="Unassigned", organisation=self.organisation)
                except Category.DoesNotExist:
                    unassigned_category = Category.objects.create(name="Unassigned", organisation=self.organisation)
                self.category = unassigned_category
            
            # Yeni kategoriler için default değerler
            if not self.source_category:
                try:
                    unassigned_source = SourceCategory.objects.get(name="Unassigned", organisation=self.organisation)
                except SourceCategory.DoesNotExist:
                    unassigned_source = SourceCategory.objects.create(name="Unassigned", organisation=self.organisation)
                self.source_category = unassigned_source
            
            if not self.value_category:
                try:
                    unassigned_value = ValueCategory.objects.get(name="Unassigned", organisation=self.organisation)
                except ValueCategory.DoesNotExist:
                    unassigned_value = ValueCategory.objects.create(name="Unassigned", organisation=self.organisation)
                self.value_category = unassigned_value
            
        super().save(*args, **kwargs)

    def __str__(self):
        name = f"{self.first_name} {self.last_name}"
        if self.email:
            return f"{name} ({self.email})"
        return name

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email

class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def is_expired(self):
        # Token 24 saat geçerli
        return timezone.now() > self.created_at + timedelta(hours=24)
    
    def __str__(self):
        return f"Verification token for {self.user.email}"

@receiver(post_save, sender=User)
def post_user_created_signal(sender, instance, created, **kwargs):
    if created:
        user_profile, created = UserProfile.objects.get_or_create(user=instance)

