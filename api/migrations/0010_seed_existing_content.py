from django.core.management import call_command
from django.db import migrations


def seed_existing_content(apps, schema_editor):
    call_command("seed_content", verbosity=0)


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0009_inquiry_service_free_text"),
    ]

    operations = [
        migrations.RunPython(seed_existing_content, migrations.RunPython.noop),
    ]
