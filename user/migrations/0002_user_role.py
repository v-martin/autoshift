# Generated by Django 5.1.6 on 2025-03-06 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('worker', 'Worker'), ('admin', 'Admin')], default='worker', max_length=10),
        ),
    ]
