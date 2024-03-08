from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Users, ServiceCategory, Service, Appointment

# Register your models here.
admin.site.register(Users)
admin.site.register(ServiceCategory)
admin.site.register(Service)
admin.site.register(Appointment)
