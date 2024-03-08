from django.shortcuts import render, redirect,  get_object_or_404
from django.http import HttpResponse, HttpResponseNotAllowed
from .forms import UserForm, ServiceForm, AddUser, AddEmployee, UpdateUser, UpdateEmployee, CategoryForm, AppointmentForm, ReviewForm, RatingEmployeeForm
from .models import Service, Users, ServiceCategory, Appointment, Review
from django.db.models import Q, Max, Avg
#for changing password
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from datetime import datetime
import time, heapq
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from datetime import date
from django.http import JsonResponse
from datetime import timedelta
from datetime import datetime
from django.utils import timezone
from itertools import groupby


def first_test(request):
    return HttpResponse('<h4>Django website...</h4>')

#register 
def register(request):
    if request.method == 'GET':
        user_form = UserForm()
        return render(request, 'register.html', {'form':user_form})
    elif request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            user_form.save()
            return redirect('login')
        else:
            return render(request, 'register.html', {'form':user_form})
    else:
        return render('<h4>It''s not possible to register!</h4>')


def index_page(request):
    categories = ServiceCategory.objects.all()
    reviews = Review.objects.all()
    
    #za prosjecnu ocjenu recenzije
    total_reviews = len(reviews)
    total_rating_sum = sum(review.mark for review in reviews)
    
    if total_reviews > 0:
        average_rating = total_rating_sum / total_reviews
        average_rating = round(average_rating, 2)
    else:
        average_rating = 0
    
    reviews_dict = {}

    for review in reviews:
        mark_star = '★' * review.mark
        reviews_dict[(mark_star, review.id)] = {
            'id': review.id,
            'text': review.text,
            'user': review.user
        }

    return render(request, 'index.html', {'categories': categories, 'dict': reviews_dict, 'average_rating': average_rating})

def delete_review(request, review_id):
    review = Review.objects.filter(id = review_id)
    if request.user.is_superuser:
        review.delete()
        return redirect('index')
    
#service creation (admin)
def add_service(request):
    if request.user.is_superuser:
        if request.method == 'GET':
            serviceForm = ServiceForm()
            return render(request, 'add_service.html', {'form': serviceForm})

        elif request.method == 'POST' and request.user.is_authenticated:
            serviceForm = ServiceForm(request.POST)
            if serviceForm.is_valid():
                serviceForm.save()
                return redirect('index')            
            else:
                return HttpResponseNotAllowed()


#service update (admin)
def update_service(request, service_id):
    service = Service.objects.get(id = service_id)

    if request.user.is_superuser:
        if request.method == 'GET':
            service_to_update = ServiceForm(instance = service)
            return render(request, 'update_service.html', {'form': service_to_update})

        elif request.method == 'POST':
            service_to_update = ServiceForm(request.POST, instance = service)
            if service_to_update.is_valid():
                service_to_update.save()
                return redirect('index') 
        
        else:
            return HttpResponse('Error!')


#delete service (admin)
def delete_service(request, service_id):
    service = Service.objects.get(id = service_id)
    service.delete()
    return redirect ('index') 

#adding users (admin)
def add_user(request):
     if request.user.is_superuser:
        if request.method == 'GET':
            userForm = AddUser()
            return render(request, 'add_user.html', {'form': userForm})

        elif request.method == 'POST' and request.user.is_authenticated:
            userForm = AddUser(request.POST)
            if userForm.is_valid():
                userForm.save()
                return redirect('users_list')            
            else:
                return HttpResponse('Error!')
      

#adding employee (admin)
def add_employee(request):
     if request.user.is_superuser:
        if request.method == 'GET':
            employeeForm = AddEmployee()
            return render(request, 'add_employee.html', {'form': employeeForm})

        elif request.method == 'POST' and request.user.is_authenticated:
            employeeForm = AddEmployee(request.POST, request.FILES or None)
            if employeeForm.is_valid():
                employee = employeeForm.save(commit=False)
                category = employeeForm.cleaned_data['category']  #dohvacanje kategorije          
                employee.save()

                #N:N table
                employee.category.set(category)
                return redirect('employees_list')             
            else:
                return HttpResponse('Error!')
      

#updating users (admin)
def update_user(request, user_id):
    user = Users.objects.get(id = user_id)

    if request.user.is_superuser:
        if request.method == 'GET':
            user_to_update = UpdateUser(instance = user)
            return render(request, 'update_user.html', {'form': user_to_update})
    
        elif request.method == 'POST':
            user_to_update = UpdateUser(request.POST, instance = user)
            if user_to_update.is_valid():
                user_to_update.save()
                return redirect('users_list') 
        else:
            return HttpResponse("Error!")

#updating employee (admin)
def update_employee(request, employee_id):
    employee = Users.objects.get(id = employee_id)

    if request.user.is_superuser:
        if request.method == 'GET':
            employee_to_update = UpdateEmployee(instance = employee)
            return render(request, 'update_employee.html', {'form': employee_to_update})
    
        elif request.method == 'POST':
            employee_to_update = UpdateEmployee(request.POST, request.FILES or None, instance = employee)
            if employee_to_update.is_valid():
                employee_to_update.save()
                return redirect('employees_list') 
        else:
            return HttpResponse("Error!")

#deleting user (admin)
def delete_user(request, user_id):
    user = Users.objects.get(id = user_id)
    user.delete()
    return redirect ('users_list') 


#deleting employee (admin)
def delete_employee(request, employee_id):
    employee = Users.objects.get(id = employee_id)
    employee.delete()
    return redirect ('employees_list') 

#list of users (admin)
def users_list(request):
    if 'q' in request.GET:
        q = request.GET['q']
        names = q.split() #splitamo po rijecima
        if len(names) >= 2:
            first_name, last_name = names[0], names[-1]
        else:
            first_name, last_name = q, q

        first_name_q = Q(first_name__icontains=first_name) # kreiranje objekta za pretrazivanje
        last_name_q = Q(last_name__icontains=last_name)
        email_q = Q(email__icontains=q)
        users = Users.objects.filter(role='user').filter(first_name_q | last_name_q | email_q)
    else:
        users = Users.objects.filter(role='user')

    return render(request, 'users_list.html', {'users':users}) 

#list of employees(admin)
def employees_list(request):
    if 'q' in request.GET:
        q = request.GET['q']
        names = q.split()
        if len(names) >= 2:
            first_name, last_name = names[0], names[-1]
        else:
            first_name, last_name = q, q

        first_name_q = Q(first_name__icontains=first_name)
        last_name_q = Q(last_name__icontains=last_name)
        email_q = Q(email__icontains=q)
        employees = Users.objects.filter(role='employee').filter(first_name_q | last_name_q | email_q)
    else:
        employees = Users.objects.filter(role = 'employee')
    return render(request, 'employees_list.html', {'employees':employees})

#adding new category (admin)
def add_category(request):
    if request.user.is_superuser:
        if request.method == 'GET':
            categoryForm = CategoryForm()
            return render(request, 'add_category.html', {'form': categoryForm})

        elif request.method == 'POST' and request.user.is_authenticated:
            categoryForm = CategoryForm(request.POST, request.FILES or None)
            if categoryForm.is_valid():
                categoryForm = ServiceCategory(name=categoryForm.cleaned_data['name'], image=categoryForm.cleaned_data['image'])
                categoryForm.save()
                return redirect('print_categories') 

#print categories
def print_categories(request):
    categories = ServiceCategory.objects.all()
    return render(request, 'print_categories.html', {'categories':categories})

#print services
def print_services(request, category_id):
    category = ServiceCategory.objects.get(id = category_id)
    services_dict = {}
    services = Service.objects.filter(category=category_id).all()
    for service in services:
        duration = service.service_duration
        service_duration_sec = duration.total_seconds() 
        service_duration_minutes = int(service_duration_sec / 60)
        services_dict[service.name] = service_duration_minutes

    #filter
    if 'min_price' in request.GET: 
        filter_price1 = request.GET.get('min_price')
        filter_price2 = request.GET.get('max_price')
        
        if filter_price2 == '':
           filter_price2 = 100 
           
        if filter_price1 == '':
            filter_price1 = 5 

        services = Service.objects.filter(category=category_id).filter(price__range=(filter_price1, filter_price2))
        #print(services)
        return render(request, 'print_services.html', {'services':services, 'category':category, 'dict':services_dict})
        
    #search
    if 'q' in request.GET:
        q = request.GET['q']

        combination = q.split()
        if len(combination) >= 2:
            name, price = combination[0], combination[-1]
        else:
            name, price = q, q

        name_q = Q(name__icontains=name)
        price_q = Q(price__icontains=price)
        services = Service.objects.filter(category=category_id).filter(name_q | price_q)
        
    else:
        services = Service.objects.filter(category=category_id)

    return render(request, 'print_services.html', {'services':services, 'category':category, 'dict':services_dict})


#price list of services
def price_list(request):
    services = Service.objects.all()
    categories = ServiceCategory.objects.all()
    return render (request, 'price_list.html', {'services':services, 'categories': categories})

 
def sort_services_asc(request, service_category_id):
    services = Service.objects.filter(category = service_category_id).order_by("name")
    category = ServiceCategory.objects.get(id = service_category_id)
    return render(request, 'print_services.html', {'services':services, 'category': category})

def sort_services_desc(request, service_category_id):
    services = Service.objects.filter(category = service_category_id).order_by("-name")
    category = ServiceCategory.objects.get(id = service_category_id)
    return render(request, 'print_services.html', {'services': services, 'category': category})


def sort_byprice_asc(request, service_category_id):
    services = Service.objects.filter(category = service_category_id).order_by("price")
    category = ServiceCategory.objects.get(id = service_category_id)
    return render(request, 'print_services.html', {'services':services, 'category': category})


def sort_byprice_desc(request, service_category_id):
    services = Service.objects.filter(category = service_category_id).order_by("-price")
    category = ServiceCategory.objects.get(id = service_category_id)
    return render(request, 'print_services.html', {'services':services, 'category': category})


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST,  error_messages={})
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})


#reservation
def reservation_service(request):
    services = Service.objects.all()
    categories = ServiceCategory.objects.all()
    return render(request, 'reservation_service.html', {"services":services, 'categories':categories})

def reservation_details(request, service_id, user_id):
    
    service = Service.objects.get(id = service_id)
    employees_list = []
    employees = Users.category.through.objects.filter(servicecategory_id = service.category)
    for e in employees:
        employees_list.append(Users.objects.get(id = e.users_id))

    if request.method == 'GET':
        return render(request, 'reservation_details.html', {'employees':employees_list, "service": service,"var_name": 20})
    
    if request.method == 'POST':
        jsonDict = {
            "service":int(request.POST.get('service')), 
            "user": request.user,
            "employee": int(request.POST.get('employee')), 
            "date": datetime.strptime(request.POST.get('date'), "%Y-%m-%d").date(),
            "time": datetime.strptime(request.POST.get('id_hours'), "%H:%M:%S").time()
        }
        form = AppointmentForm(jsonDict)   
        date2 = datetime.strptime(request.POST.get('date'), "%Y-%m-%d").date()
        form.save()
        return redirect('user_appointments_future', user_id=user_id)
    else:
        return render(request, 'reservation_details.html', {'employees':employees_list, "service": service})

def check_minutes_for_same_hours(h, minute, fill_hours):
    for hour in fill_hours:
        if hour.time.hour == h and hour.time.minute == minute:
            return False 
    return True 

def check_hours(h1, h2, fill_hours): 
    #print("OVDJE JE ", h1, " : ", h2)
    for hour in fill_hours:
        if h1.hour == hour.time.hour and h1.minute == hour.time.minute:  #zauzet je termin nemoj ga dodati
            return False
        if h1.hour == h2.hour: 
            hour_range = h2.minute - h1.minute
            for minutes in range(h1.minute, h2.minute): #je li ima zauzet termin u ovom rasponu?
                if hour.time.minute == minutes:
                    return False 
    return True

#pomocna za 30
def less_than(fill_hours, h1, h2): 
    for hour in fill_hours:
        if h1.hour == hour.time.hour and h1.minute == hour.time.minute:
            return False
    return True

def more_than_one(fill_hours, service_duration_hours, service_duration_minutes):
    new_finally = []
    final_hour = 0
    hour = datetime.strptime("08:00:00", "%H:%M:%S").time()

    while int(hour.hour) < 16:
        if int(hour.hour) + int(service_duration_minutes // 60) > 16:
            break
        new_hour2 = datetime.strptime(str(hour.hour) + ":00:00", "%H:%M:%S").time()

        total_hours = int(hour.hour) + int(service_duration_hours)
        final_hour = total_hours
        if check_hours(hour, new_hour2, fill_hours) == True:
            new_finally.append(hour)

        hour = datetime.strptime(str(total_hours) + ":00:00", "%H:%M:%S").time()  
    return new_finally


def less_than_one_hour(fill_hours, service_duration_minutes):
    hour_minutes = 0
    final_minutes = 0
    new_finally = []

    hour = datetime.strptime("08:00:00", "%H:%M:%S").time()

    while int(hour.hour) < 16:
        if int(hour.hour) + int(service_duration_minutes // 60) >= 15 and int(hour.minute) + (service_duration_minutes % 60) > 60:
            break
        new_hour2 = datetime.strptime(str(hour.hour) + ":" + str(service_duration_minutes) + ":00", "%H:%M:%S").time()

        if less_than(fill_hours, hour, new_hour2) == True:   #je li vec u zauzetim 
            new_finally.append(hour)

        new_minutes = hour.minute + int(service_duration_minutes)
        if (new_minutes >= 60):
            new_hour = int(hour.hour) + 1
            first_minutes = hour.minute + int(service_duration_minutes)
            total_minutes = first_minutes - 60
            final_minutes = total_minutes
            hour = datetime.strptime(str(new_hour) + ":" + str(total_minutes) + ":00", "%H:%M:%S").time()
        else:
            final_minutes = new_minutes
            hour = datetime.strptime(str(hour.hour) + ":" + str(new_minutes) + ":00", "%H:%M:%S").time()
        
    hour = datetime.strptime("01:" + str(final_minutes) + ":00", "%H:%M:%S").time()
    
    return new_finally

def check_hours_minutes(h1, fill_hours):  
    for hour in fill_hours:
        if h1.hour == hour.time.hour and h1.minute == hour.time.minute:
            return False  
    return True

def more_than_hour_minutes(fill_hours, service_duration_hours, service_duration_minutes):
    new_finally = []

    hour = datetime.strptime("08:00:00", "%H:%M:%S").time()
    final_minutes = 0
    final_hours = 0

    while int(hour.hour) < 16:
        if int(hour.hour) + service_duration_hours >= 16:
            break
        if int(hour.hour) + int(service_duration_minutes // 60) >= 15 and int(hour.minute) + (service_duration_minutes % 60) >= 60:
            break
        if check_hours_minutes(hour, fill_hours) == True:
            new_finally.append(hour)

        total_hours = int(hour.hour) + int(service_duration_hours)
        total_minutes = int(hour.minute) + (int(service_duration_minutes) % 60)
        if total_minutes >= 60:
            new_hour = int(total_hours) + 1
            first_minutes = hour.minute + (int(service_duration_minutes) % 60) #usluga u minutama
            sum_minutes = first_minutes - 60
            final_minutes = sum_minutes
            final_hours = new_hour
            hour = datetime.strptime(str(new_hour) + ":" + str(sum_minutes) + ":00", "%H:%M:%S").time()
        else:
            final_minutes = total_hours
            final_hours = total_hours
            hour = datetime.strptime(str(total_hours) + ":" + str(total_minutes) + ":00", "%H:%M:%S").time()

    return new_finally

def check_range(hour1, hour2, service): 
    free_hours = [] 

    service_duration2 = service.service_duration
    service_duration_sec = service_duration2.total_seconds() 
    service_duration_minutes = int(service_duration_sec / 60)
    service_duration_hours = int(service_duration_minutes / 60)

    temp = hour1.hour
    temp_minutes = hour1.minute
    if hour1.hour == hour2.hour and hour1.minute == hour2.minute:
        return free_hours

    while (temp <= hour2.hour):
        temp_minutes += service_duration_minutes

        if temp_minutes  < 60:
            potential_time = temp_minutes + service_duration_minutes #potencijalno vrijeme zavrsavanja usluge da ne prijede 16
            if potential_time >= 60:
                potential_hour = temp + 1
                potential_minute = potential_time - 60
                if ((potential_hour >= hour2.hour) and (potential_minute > hour2.minute)):  
                    return free_hours
            else:
                if temp  >= hour2.hour and potential_time > hour2.minute:
                    return free_hours
            
            new_time = datetime.strptime(str(temp) + ":" + str(temp_minutes ) + ":00", "%H:%M:%S").time()
            new_time_duration_min = new_time.minute + service_duration_minutes
            print("NOVO VRIJEME: ", new_time, " temp minute: :::", temp_minutes)
            if new_time_duration_min >= 60: 
                        new_hour = new_time.hour + 1
                        new_min = new_time_duration_min - 60
                        if new_hour > hour2.hour or (new_hour >= 16 and new_min > 0) or (new_hour > hour2.hour and new_min > hour2.minute):
                            return free_hours
                        elif ((new_hour == hour2.hour) and (new_min == hour2.minute)):  
                                 free_hours.append(new_time)
                                 return free_hours
                        else:
                            free_hours.append(new_time)
            else:
                        if new_time.hour >= 16 and new_min > 0:
                            return free_hours
                        else:
                            free_hours.append(new_time)
                
        else:  
            new_min = temp_minutes 
            temp = temp + 1
            print("NVOOOOO: ", temp, new_min)
            temp_minutes = new_min - 60
            potential_time = temp_minutes + service_duration_minutes   #zavrsavanja
            if (potential_time >= 60) and (temp + service_duration_hours < hour2.hour):
                new_time = datetime.strptime(str(temp) + ":" + str(temp_minutes % 60) + ":00", "%H:%M:%S").time()  # novo
                free_hours.append(new_time) #novo
                temp2 = temp + 1
                new_m = potential_time - 60

                if ((temp2 == hour2.hour) and (new_m > hour2.minute)):
                    return free_hours
                elif ((temp == hour2.hour) and (new_m <= hour2.minute)):
                    print("OVAJ TEMP: ", temp, temp_minutes)
                    new_time = datetime.strptime(str(temp) + ":" + str(temp_minutes) + ":00", "%H:%M:%S").time()
                    print("NOVO VRIJEME: ", new_time, " temp minute: ****", temp_minutes)
                    new_time_duration_min = new_time.minute + service_duration_minutes
                    if new_time_duration_min >= 60: 
                        new_hour = new_time.hour + 1
                        new_min = new_time_duration_min - 60
                        if new_hour > hour2.hour or (new_hour >= 16 and new_min > 0) or (new_hour > hour2.hour and new_min > hour2.minute):
                            return free_hours
                        elif ((new_hour == hour2.hour) and (new_min == hour2.minute)):  
                                free_hours.append(new_time)
                                return free_hours
                        else:
                            free_hours.append(new_time)
                    else:
                        if new_time.hour >= 16 and new_min > 0:
                            return free_hours
                        elif new_time.hour == hour2.hour and new_min == hour2.minute:
                            return free_hours
                        else:
                            free_hours.append(new_time)
                 
                   
            else:
                if ((temp > hour2.hour) or ((temp== hour2.hour) and potential_time > hour2.minute)): 
                    print("if")
                    return free_hours
                else:
                    new_time = datetime.strptime(str(temp) + ":" + str(temp_minutes) + ":00", "%H:%M:%S").time()
                   
                    new_time_duration_min = new_time.minute + service_duration_minutes
                    if new_time_duration_min >= 60: 
                        new_hour = new_time.hour + 1
                        new_min = new_time_duration_min - 60
                        if new_hour > hour2.hour or (new_hour >= 16 and new_min > 0) or (new_hour > hour2.hour and new_min > hour2.minute):
                            return free_hours
                        elif ((new_hour == hour2.hour) and (new_min == hour2.minute)):  # ne smije uci u zauzeti termin 
                                free_hours.append(new_time)
                                return free_hours
                        else:
                            free_hours.append(new_time)
                    else:
                        if new_time.hour >= 16 and new_min > 0:
                            return free_hours
                        else:
                            free_hours.append(new_time)
    return free_hours

def check_range2(hour1, hour2, service):   
    print("Ovo su sati: ", hour1, hour2)
    free_hours = [] 

    if hour1 == hour2:
        return []
    service_duration2 = service.service_duration
    service_duration_sec = service_duration2.total_seconds() 
    service_duration_minutes = int(service_duration_sec / 60)
    service_duration_hours = int(service_duration_minutes / 60)

    temp = hour1.hour
    temp_minutes = (int(service_duration_minutes) % 60)
    while (temp <= hour2.hour):
        if temp_minutes + int(service_duration_minutes) < 60:
            new_time = datetime.strptime(str(temp) + ":" + str(temp_minutes + int(service_duration_minutes)) + ":00", "%H:%M:%S").time()
            free_hours.append(new_time)
        else:  
            new_min = temp_minutes + (int(service_duration_minutes) % 60)
            temp_minutes += (int(service_duration_minutes) % 60) 
            
            temp = temp + int(service_duration_hours)  # na sate se dodaje trajanje u satima
            if (new_min >= 60):
                sum_minutes = new_min - 60
                temp = temp + 1
                temp_minutes = temp_minutes - 60
                new_time = datetime.strptime(str(temp) + ":" + str(sum_minutes) + ":00", "%H:%M:%S").time()
            else:
                new_time = datetime.strptime(str(temp) + ":" + str(temp_minutes) + ":00", "%H:%M:%S").time()
        
            new_time_duration_min = new_time.minute + service_duration_minutes
            if new_time_duration_min >= 60: 
                new_hour = new_time.hour + 1
                new_min = new_time_duration_min - 60
                if new_hour > hour2.hour or (new_hour >= 16 and new_min > 0) or (new_hour > hour2.hour and new_min > hour2.minute):
                    return free_hours
                else:
                    free_hours.append(new_time)
            else:
                if new_time.hour >= 16 and new_min > 0:
                    return free_hours
                else:
                    free_hours.append(new_time)
        temp_minutes += service_duration_minutes

    return free_hours

def fill_after2(hour2, duration, service):
    print("POCETNI ", hour2)
    free_hours = []

    service_duration2 = service.service_duration
    service_duration_sec = service_duration2.total_seconds() 
    service_duration_minutes = int(service_duration_sec / 60)
    service_duration_hours = int(service_duration_minutes / 60)

    temp = hour2.hour
    temp_minutes = hour2.minute
    while (temp < 16):
        if temp_minutes + int(duration) < 60:
            new_time = datetime.strptime(str(temp) + ":" + str(temp_minutes + int(duration)) + ":00", "%H:%M:%S").time()
            free_hours.append(new_time)
            temp_minutes += duration
        else:
            
            temp_minutes += (int(service_duration_minutes) % 60) 
            new_min =  temp_minutes
            temp = temp + int(service_duration_hours)
            print("U else ", temp, temp_minutes, new_min)
            if (new_min >= 60):
                sum_minutes = new_min - 60
                temp = temp + 1
                temp_minutes = temp_minutes - 60
                
                new_time = datetime.strptime(str(temp + service_duration_hours) + ":" + str(sum_minutes) + ":00", "%H:%M:%S").time()
                if (temp >= 16):
                    break
                print("MEW TIME: ", new_time)
                new_time_duration_min = new_time.minute 
                new_time_duration_hour = new_time.hour 
                if new_time_duration_min >= 60: 
                    print(("OVO JE TEST: ", new_time_duration_hour, new_time_duration_min))
                    new_hour = new_time.hour + new_time_duration_hour
                    new_min = new_time_duration_min - 60
                    if new_hour >= 16 and new_min > 0:
                        return free_hours
                    else:
                        free_hours.append(new_time)
                else:
                    print(("OVO JE TEST: ", new_time_duration_hour, new_time_duration_min))
                    if new_time_duration_hour + service_duration_hours >= 16:
                        return free_hours
                    else:
                        free_hours.append(new_time)
            else:
                new_time = datetime.strptime(str(temp) + ":" + str(temp_minutes) + ":00", "%H:%M:%S").time()
                new_time_duration_min = new_time.minute 
                new_time_duration_hour = new_time.hour 
                #print(("OVO JE TEST2: ", new_time_duration_hour, new_time_duration_min))
                if new_time_duration_min >= 60: 
                    new_hour = new_time.hour + new_time_duration_hour
                    new_min = new_time_duration_min - 60
                    if new_hour + service_duration_hours >= 16:
                        return free_hours
                    else:
                        free_hours.append(new_time)
                else:
                    if new_time_duration_hour + service_duration_hours >= 16:
                        return free_hours
                    else:
                        free_hours.append(new_time)
    return free_hours
        
def fill_after(hour2, duration):
    free_hours = []
    temp = hour2.hour
    temp_minutes = hour2.minute

    while (temp < 16):
        if temp_minutes + int(duration) < 60:
            new_time = datetime.strptime(str(temp) + ":" + str(temp_minutes + int(duration)) + ":00", "%H:%M:%S").time()
            temp_minutes += duration
        else:
            new_min = temp_minutes + duration
            temp = temp + 1
            temp_minutes = new_min - 60
            if (temp_minutes >= 60):
                temp_minutes = temp_minutes - 60
                temp = temp + 1
            if (temp == 16):
                   return free_hours
            new_time = datetime.strptime(str(temp) + ":" + str(temp_minutes) + ":00", "%H:%M:%S").time()
           
        new_time_duration_min = new_time.minute + duration
        if new_time_duration_min >= 60: 
                new_hour = new_time.hour + 1
                new_min = new_time_duration_min - 60
                if new_hour >= 16 and new_min > 0:
                    return free_hours
                else:
                    free_hours.append(new_time)
        else:
                if new_time.hour >= 16 and new_time_duration_min > 0:
                    return free_hours
                else:
                    free_hours.append(new_time)
    print("OVO SU OVDE SATI: ", free_hours)    
    return free_hours

def getEmployeesHours(request):
    employee = request.GET.get('employee')
    fill_hours = Appointment.objects.filter(date=request.GET.get("date")).filter(employee=employee).order_by("time").all()
    for f in fill_hours:
        print("FILL ", f.time)

    service = Service.objects.get(id = request.GET.get("service_id"))
    service_duration2 = service.service_duration
    service_duration_sec = service_duration2.total_seconds() 
    service_duration_minutes = int(service_duration_sec / 60)
    service_duration_hours = int(service_duration_minutes / 60)

    final_array = []
    hour2 = ""  # vrijeme zavrsavanja zauzetog termina
    hour2_duration = ""
    if (len(fill_hours) > 0):
        first_fill = fill_hours[0]
    else:
        first_fill = ''

    bool_flag = 0

    #8 prvi zauzeti
    if (first_fill != '' and first_fill.time.minute == 0 and first_fill.time.hour == 8): 
            fill_duration4 = Service.objects.get(id = first_fill.service.id)
            new_fill_duration4 = datetime.strptime(str(fill_duration4.service_duration), "%H:%M:%S").time() 
            sd4 = fill_duration4.service_duration
            service_duration_sec4 = sd4.total_seconds() 
            service_duration_minutes4 = int(service_duration_sec4 / 60)
            service_duration_hours4 = int(service_duration_minutes4 / 60)
            minute = service_duration_minutes4
            if minute >= 60:
                first_minutes = (int(minute) % 60)
                temp_minutes = first_minutes
                temp = first_fill.time.hour + service_duration_hours4
                prev = datetime.strptime(str(temp) + ":" + str(temp_minutes) + ":00", "%H:%M:%S").time() #novi prev
                print("PREV JE: ", prev)
                if (len(fill_hours) > 0):
                    fill_hours = fill_hours[1:]  #da krene od sata kad ovo zavrsi
            elif minute < 60:
               prev = datetime.strptime(str(first_fill.time.hour) + ":" + str(minute) + ":00", "%H:%M:%S").time() # novi prev
    else:
        prev = datetime.strptime("08:00:00", "%H:%M:%S").time() #8 nije prvi zauzet

    for element in fill_hours:
        fill_duration = Service.objects.get(id = element.service.id) 
        print("* * ", element, " traje ", fill_duration.service_duration)
        
    for fill in fill_hours: #projera preva i filla
        fill_duration = Service.objects.get(id = fill.service.id)
        new_fill_duration = datetime.strptime(str(fill_duration.service_duration), "%H:%M:%S").time() 
        sd = fill_duration.service_duration
        service_duration_sec3 = sd.total_seconds() 
        service_duration_minutes3 = int(service_duration_sec3 / 60)
        service_duration_hours3 = int(service_duration_minutes3 / 60)
        
        if (prev.minute != fill.time.minute) and (prev.hour != fill.time.hour) or (prev.minute != fill.time.minute) and (prev.hour == fill.time.hour) or (prev.minute == fill.time.minute) and (prev.hour != fill.time.hour):
            minute = prev.minute + service_duration_minutes3
            if minute >= 60:
                first_minutes = (int(service_duration_minutes3) % 60)
                temp_minutes = first_minutes
                temp = prev.hour + 1
                if temp >= fill.time.hour and temp_minutes > fill.time.minute or temp >= fill.time.hour and temp_minutes < fill.time.minute: 
                    
                    print("JE LI 10: ", prev)
                    final_array.append(prev)
                    prev = datetime.strptime(str(temp) + ":" + str(temp_minutes) + ":00", "%H:%M:%S").time()
                    #final_array.append(prev) #????
                elif temp == fill.time.hour and temp_minutes <= fill.time.minute:
                    final_array.append(prev)
                elif temp <= fill.time.hour and temp_minutes <= fill.time.minute or temp <= fill.time.hour and temp_minutes >= fill.time.minute:
                    final_array.append(prev)
            elif minute < 60:
                if prev.hour <= fill.time.hour and prev.minute >= fill.time.minute or prev.hour <= fill.time.hour and prev.minute <= fill.time.minute or prev.hour <= fill.time.hour and prev.minute >= fill.time.minute:
                    final_array.append(prev)


        if (service_duration_minutes) < 60:
                fill_duration = Service.objects.get(id = fill.service.id)
                new_fill_duration = datetime.strptime(str(fill_duration.service_duration), "%H:%M:%S").time() 
                
                if int(fill.time.minute) + int(new_fill_duration.minute) < 60: 
                    free_time = check_range(prev, fill.time, service)
                    hour2 = datetime.strptime(str(fill.time.hour) + ":" + str(int(fill.time.minute) + int(new_fill_duration.minute)) + ":00", "%H:%M:%S").time()
                else:
                    temp = fill.time.hour  
                    sum = int(fill.time.minute)
                    new_min = sum + int(new_fill_duration.minute)
                    if new_fill_duration.hour >=2: 
                            temp = temp + new_fill_duration.hour + 1  
                    else:
                        temp = temp + 1
                    sum = new_min - 60
                    free_time = check_range(prev, fill.time, service)
                    hour2 = datetime.strptime(str(temp) + ":" + str(sum) + ":00", "%H:%M:%S").time()
                    print("JE LI OVDE45 ", hour2)
                for element in free_time:
                    final_array.append(element)
        elif int(service_duration_minutes) >= 60 and int(service_duration_minutes) < 90:
                fill_duration = Service.objects.get(id = fill.service.id)
                new_fill_duration = datetime.strptime(str(fill_duration.service_duration), "%H:%M:%S").time()
                
                if (int(fill.time.minute) + int(new_fill_duration.minute)) >= 60:
                    temp_minutes = int(fill.time.minute) % 60
                    temp = fill.time.hour
                    if temp_minutes + new_fill_duration.minute >= 60:
                        new_min = temp_minutes + new_fill_duration.minute
                        if new_fill_duration.hour >=2: 
                            temp = temp + new_fill_duration.hour + 1
                        else:
                            temp = temp + 1
                        temp_minutes = new_min - 60
                        if (temp_minutes >= 60):
                            temp = temp + 1
                            temp_minutes = temp_minutes - 60
                        free_time = check_range(prev, fill.time, service) #OVO JE NOVO
                        hour2 = datetime.strptime(str(temp) + ":"+ str(temp_minutes) + ":00", "%H:%M:%S").time()
                    else:
                        temp_minutes += new_fill_duration.minute
                        hour2 = datetime.strptime(str(int(fill.time.hour) + int(new_fill_duration.hour)) + ":" + str(temp_minutes) + ":00", "%H:%M:%S").time()
                    free_time = check_range(prev, fill.time, service)
                else:
                    free_time = check_range(prev, fill.time, service)
                    hour2 = datetime.strptime(str(fill.time.hour + new_fill_duration.hour) + ":" + str(int(fill.time.minute) + int(new_fill_duration.minute)) + ":00", "%H:%M:%S").time()  #novo
                for element in free_time:
                    final_array.append(element)
        else: #vece od sat ipo
                    fill_duration = Service.objects.get(id = fill.service.id)
                    new_fill_duration = datetime.strptime(str(fill_duration.service_duration), "%H:%M:%S").time()
                    
                    if (int(fill.time.minute) + int(new_fill_duration.minute)) >= 60:
                        total_hours = int(fill.time.hour) + int(new_fill_duration.hour)
                        total_minutes = int(fill.time.minute) + (int(new_fill_duration.minute) % 60)
                        if total_minutes >= 60:
                            new_hour = int(total_hours) + 1
                            first_minutes = fill.time.minute + (int(new_fill_duration.minute) % 60)
                            sum_minutes = first_minutes - 60
                            hour2 = datetime.strptime(str(new_hour) + ":" + str(sum_minutes) + ":00", "%H:%M:%S").time()
                        else:
                            hour2 = datetime.strptime(str(total_hours) + ":" + str(total_minutes) + ":00", "%H:%M:%S").time()
                    else:
                        hour2 = datetime.strptime(str(fill.time.hour) + ":" + str(int(fill.time.minute) + int(new_fill_duration.minute)) + ":00", "%H:%M:%S").time()
                    free_time = check_range2(prev, fill.time, service)
        prev = hour2
            
    #print("LEN JE", len(fill_hours)) #ovo je ako se ne ude u for petlju da se poznaje koji je hour2
    if len(fill_hours) == 1 or len(fill_hours) == 0:
        hour2 = datetime.strptime(str(prev.hour) + ":" + str(prev.minute) + ":00", "%H:%M:%S").time()
        
    #print("OVO JE HOUR2     ", hour2)   #dodaje se hour2 u niz ako zavrsava prije 16 sati
    if hour2 not in fill_hours and hour2 != "":
        new_time_duration_min = hour2.minute + service_duration_minutes 
        new_time_duration_hour = hour2.hour + service_duration_hours
        if new_time_duration_min >= 60: 
            #new_hour = hour2.hour + service_duration_hours + 1
            new_min = new_time_duration_min - 60
            if new_time_duration_hour > 16 and new_min > 0: #vece ili jednako
                pass
            else:
                final_array.append(hour2)
        else:
            if new_time_duration_hour >= 16 and new_time_duration_min >= 0:
                pass
            else:
                final_array.append(hour2)
        

    if hour2 != "" and int(hour2.hour) < 16 and service_duration_minutes < 120:
        free_time = fill_after(hour2, service_duration_minutes)
        bool_flag = 1 #ako je jedan zauzet pa se otkine, da ne ulazi opet u liniju 929 i stvara duplikate
        for element in free_time:
            final_array.append(element)

    if hour2 != "" and int(hour2.hour) < 16 and service_duration_minutes >= 120:
        free_time = fill_after2(hour2, service_duration_minutes, service)
        bool_flag = 1
        for element in free_time:
            final_array.append(element)

    if len(fill_hours) <= 0 and bool_flag != 1:
        if int(service_duration_minutes) <= 30:
            final_array = less_than_one_hour(fill_hours, service_duration_minutes)
        elif int(service_duration_minutes) % 60 == 0:
            final_array = more_than_one(fill_hours, service_duration_hours, service_duration_minutes)
        elif int(service_duration_minutes) > 30 and int(service_duration_minutes) < 60:
            final_array = less_than_one_hour(fill_hours, service_duration_minutes)
        else:
            final_array = more_than_hour_minutes(fill_hours, service_duration_hours, service_duration_minutes)

    current_date = datetime.now().date()
    current_time = datetime.now().time()
    
    
    json_hours = [{'time': hour} for hour in final_array]

    response_data = {
        'hours': json_hours
    }
    return JsonResponse(response_data)
            

def get_user_appointments_past(request, user_id):
    current_datetime = timezone.now()

    unreviewed_appointments = Appointment.objects.filter(date__lt=current_datetime.date(), rating__isnull=True, user=user_id).order_by('-date', '-time')
    reviewed_appointments = Appointment.objects.filter(date__lt=current_datetime.date(), rating__isnull=False, user=user_id).order_by('-date', '-time')

    if request.method == 'POST':
        form = RatingEmployeeForm(request.POST)
        if form.is_valid():
            appointment_id = request.POST.get('appointment_id')
            appointment = get_object_or_404(Appointment, id=appointment_id) 
            appointment.rating = form.cleaned_data['rating'] #ocjena se sprema sprema u atribut rating objekta appointment.
            appointment.save()

            form = RatingEmployeeForm(initial={'rating': appointment.rating}) #nova instanca s početnom vrijednosti za ocjenu
    else:
        form = RatingEmployeeForm()

    return render(request, 'user_appointments_past.html', {
        'unreviewed_appointments': unreviewed_appointments,
        'reviewed_appointments': reviewed_appointments,
        'form': form
    })



def get_user_appointments_future(request, user_id):
    current_datetime = timezone.now()
    upcoming_appointments = Appointment.objects.filter(
        date__gte =current_datetime.date()) | Appointment.objects.filter(
        date=current_datetime.date(), time__gte=current_datetime.time(),
        user = user_id).order_by('date', 'time')
    
    return render(request, 'user_appointments_future.html', {'upcoming_appointments':upcoming_appointments})


def get_employees_past_appointments(request, user_id):
    current_datetime = timezone.now()

    past_appointments = Appointment.objects.filter(
        employee=user_id,
        date__lt=current_datetime.date()
    ).exclude(
        date=current_datetime.date(),
        time__gte=current_datetime.time()
    ).order_by('-date', '-time')

    grouped_past_appointments = {}
    for date, group in groupby(past_appointments, key=lambda app: app.date): #grupiranje termina s istim datumom 
        grouped_past_appointments[date] = list(group)

    return render(request, 'employee_appointments_past.html', {'grouped_past_appointments':grouped_past_appointments})


def get_employees_upcoming_appointments(request, user_id):
    current_datetime = timezone.now()

    upcoming_appointments = Appointment.objects.filter(
        employee=user_id,
        date__gte=current_datetime.date()
    ).exclude(
        date=current_datetime.date(),
        time__lt=current_datetime.time()
    ).order_by('date', 'time')

    grouped_upcoming_appointments = {}
    for date, group in groupby(upcoming_appointments, key=lambda app: app.date):
        grouped_upcoming_appointments[date] = list(group)

    return render(request, 'employee_appointments_future.html', {'grouped_upcoming_appointments':grouped_upcoming_appointments})

def delete_appointment_confirmation(request, user_id, appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return HttpResponseNotFound()  

    if request.user.is_authenticated:
        if request.user.is_authenticated and request.user.role == 'user':
            user = Appointment.objects.get(id=appointment_id, user=user_id).user
            service = Appointment.objects.get(id = appointment_id).service
            date = Appointment.objects.get(id = appointment_id).date
            time = Appointment.objects.get(id = appointment_id).time
            if request.method == 'GET':
                return render(request, 'confirm_appointment_deletion.html', { 'user':user.id, 'appointment':appointment_id, 'service':service, 'date':date, 'time':time})
        elif request.user.role == 'employee':
            user = appointment.employee
    else:
        return HttpResponse(status=401)  #nije logiran

    if request.method == 'POST':
        appointment.delete()

        if user.role == 'employee':
            appointment.send_cancellation_notification()
            return redirect('employee_appointments_future', user_id=user_id)
        
        elif user.role == 'user':
            return redirect('user_appointments_future', user_id=user_id)
    
    return render(request, 'confirm_appointment_deletion.html', {
        'user': user.id,
        'appointment': appointment_id,
        'service': appointment.service,
        'date': appointment.date,
        'time': appointment.time,
    })


def delete_appointment(request, user_id, appointment_id):
    if request.user.is_authenticated and request.user.role == 'user':
        appointment = Appointment.objects.filter(id=appointment_id, user=user_id)
        if 'yes' in request.POST:
            appointment.delete()
            return redirect('user_appointments_future', user_id=user_id)
        return redirect('user_appointments_future', user_id=user_id)
     
    elif request.user.is_authenticated and request.user.role == 'employee':
        appointment = Appointment.objects.filter(id=appointment_id, employee=user_id) 
        if 'yes' in request.POST:
            deleted_appointment = appointment.first() #dohvati prvi termin jer ih moze biti vise zbog queryseta
            appointment.delete()
            deleted_appointment.send_cancellation_notification()
            return redirect('employee_appointments_future', user_id=user_id)
        return redirect('employee_appointments_future', user_id=user_id)



def print_team(request):
    employees = Users.objects.filter(role='employee')
    dict = {}
    for employee in employees:
        categories = ServiceCategory.users.through.objects.filter(users_id=employee.id)
        service_categories = []
        for category in categories:
            service_category = ServiceCategory.objects.get(id=category.servicecategory_id)
            service_categories.append(service_category)
        dict[employee.id] = service_categories

    return render(request, 'team.html', {'employees':employees, 'dict':dict})


#zarada salona za pojedini dan
def get_daily_earnings(request):
    today = date.today()
    earnings = ( 
        Appointment.objects.filter(date__lt=today)   
        .annotate(day=TruncDate('date')) 
        .values('date')
        .annotate(earning=Sum('service__price'))
        .order_by('-date')
    )

    total_earnings = Appointment.objects.filter(date__lt=today).aggregate(total=Sum('service__price'))
    return render(request, 'daily_earnings.html', {'earnings': earnings, 'total_earnings': total_earnings})


def detail_daily_statistics(request):
    
    appointment_dates= Appointment.objects.filter(date__lt=date.today()).values('date').order_by('date').distinct()
    arr = []

    for appointment_date in appointment_dates:
        date_value = appointment_date['date']
        total_earnings = Appointment.objects.filter(date=date_value).aggregate(total_earnings=Sum('service__price'))
        best_services = Appointment.objects.filter(date=date_value).values('service__name').annotate(total_appointments=Count('service')).order_by('-total_appointments')
        best_employees = Appointment.objects.filter(date=date_value).values('employee__first_name').annotate(total_services=Count('service')).order_by('-total_services')
        arr.append({
            'date': date_value,
            'total_earnings': total_earnings,
            'best_services': best_services,
            'best_employees': best_employees
        })
    
    total_earnings = Appointment.objects.filter(date__lt=date.today()).aggregate(total=Sum('service__price'))

    return render(request, 'detail_daily_statistics.html', {'data':arr, 'total':total_earnings})

def get_best_selling_services_price(request):

    all_services = Service.objects.all()

    services_data = all_services.filter(service__date__lt=date.today() ).annotate(
        total_earnings=Sum('service__service__price'), #service - related name na appointment
        total_appointments=Count('service')
    )

    sorted_services = services_data.order_by('-total_earnings')

    return render(request, 'best_selling_services.html', {'services':sorted_services, 'today':date.today()})


#usluge poredane po broju odradenih usluga
def get_best_selling_services_num(request):
    all_services = Service.objects.all()

    services_data = all_services.filter(service__date__lt=date.today() ).annotate(
        total_earnings=Sum('service__service__price'),
        total_appointments=Count('service')
    )

    sorted_services = services_data.order_by('-total_appointments')

    return render(request, 'best_selling_services.html', {'services':sorted_services, 'today':date.today()})

def get_all_performed_services(request):
    all_services = Service.objects.all()

    services_data = all_services.filter(service__date__lt=date.today() ).annotate(
        total_earnings=Sum('service__service__price'), 
        total_appointments=Count('service')
    )
    return render(request, 'best_selling_services.html', {'services': services_data, 'today':date.today()})

#pregled zaposlenika koji ostvaruju najveci promet
def get_employee_statistics(request):
    employees = Users.objects.filter(role='employee')

    employees_data = employees.annotate(
        total_earnings = Sum('employee_appointments__service__price'),
        total_services = Count('employee_appointments')
    )

    sorted_employees = employees_data.order_by('-total_earnings')

    return render(request, 'employee_statistics.html', {'employees': sorted_employees, 'today': date.today()})


def add_review(request):
    if request.method == 'GET':
        reviewForm = ReviewForm(user=request.user)
        return render(request, 'add_review.html', {'form': reviewForm})

    elif request.method == 'POST' and request.user.is_authenticated:
        reviewForm = ReviewForm(request.POST, user=request.user)
        if reviewForm.is_valid():
            reviewForm.save()
            return redirect('index')            
        else:
            return HttpResponseNotAllowed()


def calculate_average_rating_by_employee_in_year(year):
    employees = Users.objects.filter(employee_appointments__date__year=year).distinct() #korisnici sa terminima u toj godini
    average_ratings_by_employee = {}

    for employee in employees:
        appointments = Appointment.objects.filter(employee=employee, date__year=year, rating__isnull=False) #termini koji imaju ocjenu
        average_rating = appointments.aggregate(avg_rating=Avg('rating'))['avg_rating'] 

        if average_rating is not None:
            average_rating = round(average_rating, 2)

        average_ratings_by_employee[employee] = average_rating

    return average_ratings_by_employee

def get_top_three_employees(average_ratings_by_employee):
    top_three_employees = heapq.nlargest(3, average_ratings_by_employee.items(), key=lambda item: item[1] or 0) 
    return top_three_employees


def calculate_average_rating_by_employee_in_quarter(year, quarter):
    employees = Users.objects.filter(employee_appointments__date__year=year).distinct()
    average_ratings_by_employee = {}

    quarters = {
        1: (1, 3),
        2: (4, 6),
        3: (7, 9),
        4: (10, 12),
    }

    start_month, end_month = quarters[quarter] 
    start_date = datetime(year, start_month, 1) 
    end_date = datetime(year, end_month, 1).replace(day=28) 

    for employee in employees:
        appointments = Appointment.objects.filter(employee=employee, date__range=(start_date, end_date), rating__isnull=False)
        average_rating = appointments.aggregate(avg_rating=Avg('rating'))['avg_rating']

        if average_rating is not None and average_rating > 0:
            average_rating = round(average_rating, 2)
            average_ratings_by_employee[employee] = average_rating

    return average_ratings_by_employee

def average_rating_by_employee_quarter(request):
    current_year = datetime.now().year

    average_ratings = calculate_average_rating_by_employee_in_year(current_year)
    top_three_employees = get_top_three_employees(average_ratings)

    quarterly_ratings = {}

    for quarter in range(1, 5):
        average_ratings_quarter = calculate_average_rating_by_employee_in_quarter(current_year, quarter)
        top_three_employees_quarter = get_top_three_employees(average_ratings_quarter)
        quarterly_ratings[quarter] = top_three_employees_quarter

    return render(request, 'average_rating_by_employee_quarter.html', {
        'current_year': current_year,
        'average_ratings': average_ratings,
        'top_three_employees': top_three_employees,
        'quarterly_ratings': quarterly_ratings
    })


