# Generated by Django 4.0.5 on 2023-02-25 18:49

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0026_remove_service_employee_servicecategory_employee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicecategory',
            name='employee',
            field=models.ManyToManyField(related_name='users', to=settings.AUTH_USER_MODEL),
        ),
    ]
