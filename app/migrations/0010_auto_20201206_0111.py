# Generated by Django 2.2.17 on 2020-12-05 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20201205_2145'),
    ]

    operations = [
        migrations.AddField(
            model_name='compliancerecord',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='compliancerecordentry',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='personnel',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
