# Generated migration to update default language to English

from django.db import migrations


def update_existing_users_to_english(apps, schema_editor):
    """Update existing users without language or with 'fa' to 'en'"""
    CustomUser = apps.get_model('main', 'CustomUser')
    # Update users with no language or 'fa' to 'en'
    CustomUser.objects.filter(language__isnull=True).update(language='en')
    CustomUser.objects.filter(language='fa').update(language='en')


def reverse_update(apps, schema_editor):
    """Reverse migration - set back to 'fa'"""
    CustomUser = apps.get_model('main', 'CustomUser')
    CustomUser.objects.filter(language='en').update(language='fa')


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_customuser_language'),
    ]

    operations = [
        migrations.RunPython(update_existing_users_to_english, reverse_update),
    ]
