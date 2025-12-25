# Generated manually for adding created_at and updated_at fields

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
        ),
        migrations.AddField(
            model_name='file',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]

