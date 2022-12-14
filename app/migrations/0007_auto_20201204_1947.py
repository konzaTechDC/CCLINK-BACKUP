# Generated by Django 2.2.17 on 2020-12-04 16:47

from django.db import migrations, models
import jsignature.fields
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20201204_1912'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personnel',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='personnel',
            name='first_name',
            field=models.CharField(blank=True, error_messages={'max_length': 'The first name is too long. Use a maximum of 200 characters.'}, max_length=200, null=True, verbose_name='first name'),
        ),
        migrations.AlterField(
            model_name='personnel',
            name='other_name',
            field=models.CharField(blank=True, error_messages={'max_length': 'The other name is too long. Use a maximum of 200 characters.'}, max_length=200, null=True, verbose_name='other name'),
        ),
        migrations.AlterField(
            model_name='personnel',
            name='signature',
            field=jsignature.fields.JSignatureField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='personnel',
            name='tel_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None),
        ),
        migrations.AlterField(
            model_name='personneldesignation',
            name='designation_name',
            field=models.CharField(blank=True, error_messages={'max_length': 'The designation name is too long. Use a maximum of 200 characters.'}, max_length=200, null=True, verbose_name='designation name'),
        ),
        migrations.AlterField(
            model_name='personneldesignation',
            name='type',
            field=models.CharField(blank=True, choices=[('CONSTRUCTION SUPERVISING CONSULTANT???S / PROFFESSIONALS', 'CONSTRUCTION SUPERVISING CONSULTANT???S / PROFFESSIONALS'), ('CONSTRUCTION CONTRACTOR???S PERSONNEL', 'CONSTRUCTION CONTRACTOR???S PERSONNEL')], error_messages={'max_length': 'The type is too long. Use a maximum of 200 characters.'}, max_length=200, null=True, verbose_name='type'),
        ),
    ]
