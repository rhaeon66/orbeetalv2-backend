from django.db import migrations, models

import api.models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0015_client_website_links"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepagecontent",
            name="brand_logo",
            field=models.ImageField(
                blank=True,
                upload_to=api.models.homepage_logo_upload,
                validators=[api.models.validate_image_file],
            ),
        ),
        migrations.AddField(
            model_name="homepagecontent",
            name="brand_logo_fallback",
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name="homepagecontent",
            name="contact_email",
            field=models.EmailField(blank=True, default="support@orbeetal.com", max_length=254),
        ),
        migrations.AddField(
            model_name="homepagecontent",
            name="contact_phone",
            field=models.CharField(blank=True, default="+88 01627480049", max_length=40),
        ),
        migrations.AddField(
            model_name="homepagecontent",
            name="contact_website",
            field=models.CharField(blank=True, default="www.orbeetal.com", max_length=255),
        ),
    ]
