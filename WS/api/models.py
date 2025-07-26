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
    Modèle Custom pour l'utilisateur.
    """

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, blank=False, default="H")

    # L'email sera utilisé comme identifiant au lieu du username
    USERNAME_FIELD = "email"

    # Champs requis lors de la création d'un utilisateur
    REQUIRED_FIELDS = ["username", "first_name", "last_name", "gender", "birth_date"]

    def __str__(self):
        """
        Affiche l'email lorsqu'on convertit un utilisateur en str
        """
        return self.email


class EmailVerificationCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
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
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
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
