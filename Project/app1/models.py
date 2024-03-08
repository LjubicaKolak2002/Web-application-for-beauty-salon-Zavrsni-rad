from django.db import models
from django.contrib.auth.models import AbstractUser
from phone_field import PhoneField
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings

# Create your models here.
    
class ServiceCategory(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/', blank=True)
    
    def __str__(self):
        return ' %s' % (self.name)


class Users(AbstractUser):
    email = models.EmailField()
    ROLES = (('employee', 'employee'), ('user', 'user'))
    role = models.CharField(max_length=50, choices=ROLES)
    phone = PhoneField(blank = True)
    category = models.ManyToManyField(ServiceCategory, related_name='users')
    image = models.ImageField(upload_to='images/', blank=True)

    def __str__(self):
        return ' %s %s' % (self.first_name, self.last_name)


class Service(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, blank=True, null=True) #stupac u bazi moze biti prazan
    service_duration = models.DurationField()

    def __str__(self):
        return ' %s' % (self.name)


class Appointment(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, related_name='service')
    time_ordered = models.DateTimeField(default=datetime.now, blank=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, blank=True, related_name='user_appointments')
    employee = models.ForeignKey(Users, on_delete=models.CASCADE, blank=True, null=True, related_name='employee_appointments') 
    date = models.DateField(auto_now=False, auto_now_add=False)
    time = models.TimeField(auto_now=False, auto_now_add=False)
    rating = models.PositiveIntegerField(choices=((1, '★'), (2, '★★'), (3, '★★★'), (4, '★★★★'), (5, '★★★★★')), null=True, blank=True)

    
    def __str__(self):
        return '%s %s %s %s %s %s' % (self.user, self.service, self.date, self.time, self.time_ordered, self.employee)
    
    def send_cancellation_notification(self):
        subject = "Appointment cancelled"
        message = f"Dear {self.user}, \nYour  appointment for the {self.service} service on the day {self.date} - {self.time} has been canceled due to the inability of the employee {self.employee}.\n We apologize and best regards!\n Your salon, Beauty Time"

        # Send the email
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [self.user.email],
            fail_silently=False, #iznimka u slucaju pogreske
        )
    
    
class Review(models.Model):
    user =  models.ForeignKey(Users, on_delete=models.CASCADE, null=True, blank=True, related_name = 'user_review')
    time = models.DateTimeField(default=datetime.now, blank=True)
    text = models.TextField()
    mark = models.PositiveIntegerField(default=5)

    def __str__(self):
        return '%s %s %s' % (self.user, self.text, self.time)
    

