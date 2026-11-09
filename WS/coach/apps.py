from django.apps import AppConfig


class CoachConfig(AppConfig):
    """Nutrition coach: food catalogue, daily targets and weekly meal plans."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "coach"
    verbose_name = "Coach nutrition"
