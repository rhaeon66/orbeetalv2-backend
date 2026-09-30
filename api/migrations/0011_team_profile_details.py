from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0010_seed_existing_content"),
    ]

    operations = [
        migrations.AddField(
            model_name="teammember",
            name="phone",
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name="teammember",
            name="location",
            field=models.CharField(blank=True, max_length=160),
        ),
        migrations.AddField(
            model_name="teammember",
            name="website",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="teammember",
            name="linkedin",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="teammember",
            name="github",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="teammember",
            name="facebook",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="teammember",
            name="instagram",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="teammember",
            name="x_url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="teammember",
            name="youtube",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="teammember",
            name="behance",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="teammember",
            name="dribbble",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="teammember",
            name="portfolio",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="teammember",
            name="details",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
