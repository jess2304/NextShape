import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    """
    Modèle Custom pour l'utilisateur.
    """

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    # L'email sera utilisé comme identifiant au lieu du username
    USERNAME_FIELD = "email"

    # Champs requis lors de la création d'un utilisateur
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

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
