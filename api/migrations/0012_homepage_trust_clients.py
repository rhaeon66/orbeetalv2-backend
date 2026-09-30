from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0011_team_profile_details"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepagecontent",
            name="trust_client_ids",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
