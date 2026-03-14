import datetime

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

ACTIVITY_CHOICES = [
    ("sedentaire", "Sédentaire"),
    ("leger", "Léger"),
    ("modere", "Modéré"),
    ("intense", "Intense"),
    ("tres_intense", "Très intense"),
]


class CustomUser(AbstractUser):
    """
    Custom user model.
    """

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, blank=False, default="H")
    # Use email as the unique login identifier instead of username
    USERNAME_FIELD = "email"
    # Required fields when creating a user
    REQUIRED_FIELDS = ["username", "first_name", "last_name", "gender", "birth_date"]

    def __str__(self):
        """
        Return the email when converting the user to string.
        """
        return self.email


class EmailVerificationCode(models.Model):
    CONTEXT_CHOICES = [
        ("registration", "registration"),
        ("reset_password", "reset_password"),
    ]

    email = models.EmailField()
    code = models.CharField(max_length=6)
    context = models.CharField(max_length=20, choices=CONTEXT_CHOICES)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return self.created_at < timezone.now() - datetime.timedelta(minutes=10)

    def __str__(self):
        return f"{self.email} - {self.code}"


class ProgressRecord(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="progress_records",
    )
    date = models.DateField(default=timezone.now)
    weight_kg = models.FloatField()
    height_cm = models.FloatField()
    activity_level = models.CharField(
        max_length=20,
        choices=ACTIVITY_CHOICES,
        default="modere",
    )
    imc = models.FloatField()
    bmr = models.FloatField()
    tdee = models.FloatField()
    calories_recommandees = models.FloatField()
    goal = models.CharField(max_length=20)
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateField(auto_now=True)

    class Meta:
        unique_together = ("user", "date")
        ordering = ["-date"]


class UserNutritionPreferences(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="nutrition_preferences",
    )
    allergies = models.TextField(blank=True, default="")
    diet_type = models.CharField(max_length=50, blank=True, default="")
    disliked_foods = models.TextField(blank=True, default="")
    supplements = models.JSONField(default=list, blank=True)
    meals_per_day = models.IntegerField(default=3)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserWeekNutritionPlan(models.Model):
    """
    One stored weekly nutrition plan per user.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="week_nutrition_plan",
    )
    plan_payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"WeekPlan<{self.user_id}>"
