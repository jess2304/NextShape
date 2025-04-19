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
