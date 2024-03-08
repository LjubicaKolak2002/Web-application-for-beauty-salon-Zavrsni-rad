# Generated by Django 4.0.5 on 2023-07-25 08:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0064_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='rating',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='EmployeeMark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mark', models.IntegerField(choices=[(1, '★'), (2, '★★'), (3, '★★★'), (4, '★★★★'), (5, '★★★★★')])),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_mark', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]