# Generated by Django 4.0.5 on 2023-02-20 20:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0019_employee_service'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categories', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app1.servicecategory')),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Employee_Service',
        ),
    ]
