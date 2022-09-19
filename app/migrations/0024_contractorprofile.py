# Generated by Django 2.2.17 on 2021-01-17 16:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0023_auto_20210117_1051'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContractorProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(error_messages={'max_length': 'The company name is too long. Use a maximum of 200 characters.'}, max_length=200, verbose_name='company name')),
                ('type', models.CharField(choices=[('Construction', 'Construction'), ('ICT', 'ICT')], error_messages={'max_length': 'The type is too long. Use a maximum of 200 characters.'}, max_length=200, verbose_name='type')),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project_manager', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
