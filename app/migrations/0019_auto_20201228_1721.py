# Generated by Django 2.2.17 on 2020-12-28 14:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0018_auto_20201227_2144'),
    ]

    operations = [
        migrations.AddField(
            model_name='compliancerecordentry',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='compliancerecordentry',
            name='deleted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='deleted_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='compliancerecordentry',
            name='evaluated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='evaluated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='compliancerecordentry',
            name='submitted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='submitted_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='compliancerecordentry',
            name='last_updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='last_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='compliancerecordentry',
            name='project_name',
            field=models.CharField(error_messages={'max_length': 'The name is too long. Use a maximum of 200 characters.'}, max_length=200, verbose_name='project_name'),
        ),
    ]
