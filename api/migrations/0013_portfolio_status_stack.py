from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0012_homepage_trust_clients"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="status",
            field=models.CharField(
                choices=[
                    ("finished", "Finished"),
                    ("running", "Running"),
                    ("upcoming", "Upcoming"),
                ],
                default="finished",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="project_type",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="project",
            name="stack",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="product",
            name="project_type",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="product",
            name="stack",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
