# Generated by Django 4.1.3 on 2023-07-21 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='interview',
            name='panelist_invitation_letter',
            field=models.TextField(default='N/A'),
        ),
    ]
