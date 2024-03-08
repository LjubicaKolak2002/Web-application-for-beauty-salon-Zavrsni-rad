from django.shortcuts import redirect


def employee_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.role == 'employee' or request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:
            return redirect('index')
    return wrap


def user_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.role == 'student' or request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:
            return redirect('index')
    return wrap


def admin_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:
            return redirect('index')
    return wrap



