# Generated by Django 4.0.5 on 2023-02-24 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0021_remove_service_employee_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicecategory',
            name='image',
            field=models.ImageField(blank=True, upload_to='images/'),
        ),
    ]