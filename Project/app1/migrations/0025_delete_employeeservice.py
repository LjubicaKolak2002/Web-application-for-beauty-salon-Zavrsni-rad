# Generated by Django 4.0.5 on 2023-02-25 18:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0024_remove_users_category_service_employee'),
    ]

    operations = [
        migrations.DeleteModel(
            name='EmployeeService',
        ),
    ]
