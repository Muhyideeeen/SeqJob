# Generated by Django 4.1.3 on 2023-10-30 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myauthentication', '0004_alter_companyprofile_industry_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobseekerprofile',
            name='linkdin',
            field=models.TextField(blank=True, default='Null', null=True),
        ),
        migrations.AlterField(
            model_name='jobseekerprofile',
            name='twitter',
            field=models.TextField(blank=True, default='Null', null=True),
        ),
    ]
