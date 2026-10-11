from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0004_userweeknutritionplan"),
    ]

    operations = [
        migrations.AddField(
            model_name="progressrecord",
            name="calculation_age",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="progressrecord",
            name="calculation_gender",
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
    ]
