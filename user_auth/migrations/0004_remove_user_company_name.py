# Generated by Django 2.2.17 on 2021-01-17 17:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth', '0003_auto_20210117_1924'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='company_name',
        ),
    ]
