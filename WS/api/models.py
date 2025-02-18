from django.contrib.auth.models import User
from django.db import models


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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight = models.FloatField()
    height = models.FloatField()
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[("M", "Homme"), ("F", "Femme")])
    activity_level = models.CharField(max_length=50, choices=ACTIVITY_LEVEL_CHOICES)
    creation_date = models.DateTimeField(auto_now_add=True)
