# Generated by Django 2.2.17 on 2020-12-19 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_auto_20201219_1856'),
    ]

    operations = [
        migrations.AddField(
            model_name='compliancerequirementmetric',
            name='input_type',
            field=models.CharField(choices=[('text', 'text'), ('int', 'int')], default='text', error_messages={'max_length': 'The type is too long. Use a maximum of 200 characters.'}, max_length=200, verbose_name='type'),
        ),
        migrations.AddField(
            model_name='compliancerequirementmetric',
            name='is_required',
            field=models.BooleanField(default=True, verbose_name='is_required'),
        ),
    ]