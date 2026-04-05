from django.db import models
from django.contrib.auth.models import User


class User_Data(models.Model):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("user", "User"),
    ]

    NOTIFICATION_CHOICES = [
        ("email", "Email"),
        ("sms", "SMS"),
        ("push", "Push"),
    ]

    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_data", default=0
    )
    mobile = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=False)
    is_active = models.BooleanField(default=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    profile_picture_url = models.CharField(max_length=500, blank=True, null=True)
    preferred_notification = models.CharField(
        max_length=20, choices=NOTIFICATION_CHOICES, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user}"

    class Meta:
        db_table = "users"
