import random
from datetime import datetime, timedelta

from api.models import ProgressRecord
from api.utils import calculs_calories
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
                "gender": "H",
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
        age = 25
        for i in range(60):
            date = base_date + timedelta(days=i)
            weight = 86.5 - i * 0.1 + random.uniform(-0.3, 0.3)
            height = 175
            goal = random.choice(["maintien", "prise", "perte"])
            activity_level = random.choice(list(ACTIVITY_FACTORS.keys()))

            result = calculs_calories(weight, height, age, user.gender, activity_level, goal)  # type: ignore

            ProgressRecord.objects.create(
                user=user,
                date=date,
                weight_kg=round(weight, 1),
                height_cm=height,
                activity_level=activity_level,
                imc=result["imc"],
                bmr=result["bmr"],
                tdee=result["tdee"],
                calories_recommandees=result["calories_recommandees"],
                goal=goal,
            )
        self.stdout.write(self.style.SUCCESS("60 progress records added."))
