import random
from datetime import datetime, timedelta

from api.models import ProgressRecord
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

ACTIVITY_FACTORS = {
    "sedentaire": 1.2,
    "leger": 1.375,
    "modere": 1.55,
    "intense": 1.725,
    "tres_intense": 1.9,
}


class Command(BaseCommand):
    help = "Seed database with fake users and progress records"

    def handle(self, *args, **kwargs):
        user, created = User.objects.get_or_create(
            email="jessem@mail.com",
            defaults={
                "username": "jessem@mail.com",
                "first_name": "Jessem",
                "last_name": "Ettaghouti",
                "phone_number": "0600000000",
                "birth_date": "1999-09-05",
            },
        )
        if created:
            user.set_password("123")
            user.save()
            self.stdout.write(self.style.SUCCESS("User created."))
        else:
            self.stdout.write(self.style.WARNING("User already exists."))

        # Création des données de progression
        ProgressRecord.objects.filter(user=user).delete()

        base_date = datetime.now() - timedelta(days=60)
        for i in range(60):
            date = base_date + timedelta(days=i)
            weight = 86.5 - i * 0.1 + random.uniform(-0.3, 0.3)
            height = 175  # cm
            imc = weight / ((height / 100) ** 2)
            goal = random.choice(["maintain", "gain", "lose"])

            # BMR (Harris-Benedict simple, homme de 25 ans)
            bmr = 10 * weight + 6.25 * height - 5 * 25 + 5

            # Activité aléatoire
            activity_level = random.choice(list(ACTIVITY_FACTORS.keys()))
            activity_factor = ACTIVITY_FACTORS[activity_level]

            tdee = bmr * activity_factor

            if goal == "lose":
                calories = tdee - 500
            elif goal == "gain":
                calories = tdee + 300
            else:
                calories = tdee

            ProgressRecord.objects.create(
                user=user,
                date=date,
                weight_kg=round(weight, 1),
                height_cm=height,
                activity_level=activity_level,
                imc=round(imc, 2),
                bmr=round(bmr, 2),
                tdee=round(tdee, 2),
                calories_recommandees=round(calories, 2),
                goal=goal,
            )
        self.stdout.write(self.style.SUCCESS("60 progress records added."))
