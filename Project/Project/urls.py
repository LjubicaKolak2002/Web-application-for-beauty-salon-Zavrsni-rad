"""Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app1 import views
from django.contrib.auth.views import LoginView, LogoutView
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('first_test/', views.first_test, name='first_test'), 
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('register/', views.register, name='register'), 
    path('index/', views.index_page, name='index'), 
    path('add_service/', views.add_service, name='add_service'), 
    path('update_service/<int:service_id>/', views.update_service, name='update_service'),
    path('delete_service/<int:service_id>/', views.delete_service, name = 'delete_service'), 
    path('add_user/', views.add_user, name = 'add_user'), 
    path('add_employee/', views.add_employee, name = 'add_employee'), 
    path('update_user/<int:user_id>/', views.update_user, name = 'update_user'), 
    path('update_employee/<int:employee_id>/', views.update_employee, name = 'update_employee'),
    path('delete_user/<int:user_id>/', views.delete_user, name = 'delete_user'),  
    path('delete_employee/<int:employee_id>/', views.delete_employee, name = 'delete_employee'),
    path('users_list/', views.users_list, name = 'users_list'), 
    path('employees_list/', views.employees_list, name = 'employees_list'), 
    path('logout/', LogoutView.as_view(template_name='index.html'), name='logout'), 
    path('add_category/', views.add_category, name = 'add_category'), 
    path('print_categories/', views.print_categories, name = 'print_categories'), 
    path('print_services/<int:category_id>/', views.print_services, name = 'print_services'), 
    path('price_list/', views.price_list, name = 'price_list'), 
    path('sort_services_asc/<int:service_category_id>/', views.sort_services_asc, name = 'sort_services_asc'),
    path('sort_services_desc/<int:service_category_id>/', views.sort_services_desc, name = 'sort_services_desc'),
    path('sort_byprice_asc/<int:service_category_id>/', views.sort_byprice_asc, name = 'sort_byprice_asc'),
    path('sort_byprice_desc/<int:service_category_id>/', views.sort_byprice_desc, name = 'sort_byprice_desc'),
    path('change_password/', views.change_password, name = 'change_password'),
    path('our_team/', views.print_team, name = 'our_team'),
    path('reservation_service/', views.reservation_service, name = 'reservation_service'),
    path('reservation_details/<int:service_id>/<int:user_id>', views.reservation_details, name = 'reservation_details'),
    path('daily_earnings/', views.get_daily_earnings, name = 'daily_earnings'),
    path('best_selling_services_price/', views.get_best_selling_services_price, name = 'best_selling_services_price'),
    path('best_selling_services_num/', views.get_best_selling_services_num, name = 'best_selling_services_num'),
    path('best_selling_services/', views.get_all_performed_services, name = 'best_selling_services'),
    path('employee_statistics/', views.get_employee_statistics, name = 'employee_statistics'),
    path('detail_daily_statistics/', views.detail_daily_statistics, name = 'detail_daily_statistics'),
    path('get_hours/', views.getEmployeesHours, name='get_employees_hours'),
    path('delete_appointment_confirmation/<int:user_id>/<int:appointment_id>', views.delete_appointment_confirmation, name='delete_appointment_confirmation'),
    path('user_appointments_past/<int:user_id>', views.get_user_appointments_past, name = 'user_appointments_past'),
    path('user_appointments_future/<int:user_id>', views.get_user_appointments_future, name = 'user_appointments_future'),
    path('add_review/', views.add_review, name = 'add_review'),
    path('delete_review/<int:review_id>', views.delete_review, name = 'delete_review'),
    path('average_rating_by_employee_quarter/', views.average_rating_by_employee_quarter, name = 'average_rating_by_employee_quarter'),
    path('delete_appointment/<int:user_id>/<int:appointment_id>', views.delete_appointment, name='delete_appointment'),
    path('employee_appointments_past/<int:user_id>', views.get_employees_past_appointments, name='employee_appointments_past'),
    path('employee_appointments_future/<int:user_id>', views.get_employees_upcoming_appointments, name='employee_appointments_future')
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

