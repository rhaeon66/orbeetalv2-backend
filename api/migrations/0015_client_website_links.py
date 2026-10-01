from django.db import migrations

# Sites already stored on the matching client projects. Only fills a blank link.
CLIENT_URLS = {
    "Ruet Reporters Unity": "https://www.rru24.com",
    "Airy International": "https://www.airyfiltration.com.bd",
    "Cleanroom AC": "https://www.cleanroomac.com",
    "MUNA": "https://www.munabooks.com",
    "CloudX Academy": "https://www.cloudx.academy",
    "July Heroes": "https://www.julyheroes.com",
}


def fill_blank_client_urls(apps, schema_editor):
    Client = apps.get_model("api", "Client")
    for name, url in CLIENT_URLS.items():
        Client.objects.filter(name=name, url="").update(url=url)


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0014_technology_catalog"),
    ]

    operations = [
        migrations.RunPython(fill_blank_client_urls, migrations.RunPython.noop),
    ]
