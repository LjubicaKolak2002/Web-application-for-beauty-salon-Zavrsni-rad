from django.forms import ModelForm
from .models import Users, Service, ServiceCategory, Appointment, Review
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms.widgets import DateInput
from datetime import date
from dateutil.relativedelta import relativedelta
import django_filters


# registration form
class UserForm(UserCreationForm):
    class Meta:
        model = Users
        fields = [
            'username', 
            'first_name',
            'last_name',
            'phone',  
      ]

    def __init__(self, *args, **kwargs):
      super(UserForm, self).__init__(*args, **kwargs)
      for field in self.fields:
         self.fields[field].widget.attrs['class'] = 'updateForm'
         self.fields[field].help_text = ''


#form for adding new service      
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'price', 'category', 'service_duration']
    

#form for adding new user (admin)
class AddUser(UserCreationForm):
    ROLES = (('user', 'user'),)
    role = forms.ChoiceField(choices = ROLES)
    username = forms.CharField(
        max_length=150,
        error_messages={} 
    )
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput,
        error_messages={
            'required': 'You must enter a password.',
            'password_mismatch': 'Passwords do not match.',
        }
    )
    
    password2 = forms.CharField(
        label="Confirm password",
        strip=False,
        widget=forms.PasswordInput,
        error_messages={
            'required': 'You must confirm your password.',
        }
    )

    class Meta:
        model = Users
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'role']
        

#form for adding new employee (admin)
class AddEmployee(UserCreationForm):
    ROLES = (('employee', 'employee'),)
    role = forms.ChoiceField(choices = ROLES)
    username = forms.CharField(
        max_length=150,
        error_messages={} 
    )
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput,
        error_messages={
            'required': 'You must enter a password.',
            'password_mismatch': 'Passwords do not match.',
        }
    )
    
    password2 = forms.CharField(
        label="Confirm password",
        strip=False,
        widget=forms.PasswordInput,
        error_messages={
            'required': 'You must confirm your password.',
        }
    )

    class Meta:
        model = Users
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'role', 'category', 'image']

    category = forms.ModelMultipleChoiceField(
        queryset=ServiceCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
       


#form for updating user (admin)
class UpdateUser(ModelForm):
    ROLES = (('user', 'user'),)
    role = forms.ChoiceField(choices = ROLES)
    username = forms.CharField(
        max_length=150,
        error_messages={} 
    )

    class Meta:
        model = Users
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'role']


#form for updating employee (admin)
class UpdateEmployee(ModelForm):
    ROLES = (('employee', 'employee'),)
    role = forms.ChoiceField(choices = ROLES)
    username = forms.CharField(
        max_length=150,
        error_messages={} 
    )

    class Meta:
        model = Users
        fields = ['username', 'first_name', 'last_name', 'email', 'phone' ,'role', 'category', 'image']
    
    category = forms.ModelMultipleChoiceField(
        queryset=ServiceCategory.objects.all(),
       widget=forms.CheckboxSelectMultiple
    )

#form for adding new category
class CategoryForm(ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ['name', 'image']


class DateInput(forms.DateInput):
    input_type = 'date'

class AppointmentForm(ModelForm):
    class Meta:
        model = Appointment
        fields = ['service', 'user', 'employee', 'date', 'time']
        widgets = {'date': DateInput(),}

    date = forms.DateField(widget=DateInput(attrs={'type': 'date', 'class': 'datepicker'}))

    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['min'] = str(date.today())
        self.fields['date'].widget.attrs['max'] = str(date.today() + relativedelta(months=3))
        self.fields['date'].initial = date.today()



#form for adding new recension
class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['user', 'text', 'mark']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()

    def save(self, commit=True):
        instance = super(ReviewForm, self).save(commit=False)
        instance.user = self.user
        if commit:
            instance.save()
        return instance


class RatingEmployeeForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['rating']