from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


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


class HealthRecord(models.Model):
    """
    Informations de santé de l'utilisateur
    -Le poids est en Kg
    -La taille est en cm
    """

    ACTIVITY_LEVEL_CHOICES = [
        ("sedentary", "Sédentaire (peu ou pas d'exercice)"),
        ("light", "Léger (1-3 séances de sport par semaine)"),
        ("moderate", "Modéré (3-5 séances de sport par semaine)"),
        ("active", "Actif (sport quotidien ou travail physique)"),
        ("very_active", "Très actif (athlète ou métier très physique)"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    weight = models.FloatField()
    height = models.FloatField()
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[("M", "Homme"), ("F", "Femme")])
    activity_level = models.CharField(max_length=50, choices=ACTIVITY_LEVEL_CHOICES)
    creation_date = models.DateTimeField(auto_now_add=True)
