# Generated by Django 4.0.5 on 2023-02-08 19:52

from django.db import migrations
import phone_field.models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0008_alter_users_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='phone',
            field=phone_field.models.PhoneField(blank=True, max_length=31),
        ),
    ]