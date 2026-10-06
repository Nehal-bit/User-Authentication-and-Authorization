from django.db import migrations

def create_roles(apps, schema_editor):
    Role = apps.get_model("authz", "Role")
    Role.objects.get_or_create(name="ADMIN")
    Role.objects.get_or_create(name="USER")

class Migration(migrations.Migration):

    dependencies = [
        ('authz', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_roles),
    ]
