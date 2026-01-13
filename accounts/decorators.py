from django.shortcuts import redirect

def manager_required(view_func):
    def wrapper(request,*args,**kwargs):
        if hasattr(request.user, 'managerprofile'):
            return view_func(request, *args,**kwargs)
        else:
            return redirect('student_dashboard')
    return wrapper

def student_required(view_func):
    def wrapper(request,*args,**kwargs):
        if hasattr(request.user,'studentprofile'):
            return view_func(request,*args,**kwargs)
        else:
            return redirect('manager_dashboard')
    return wrapper

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('login')
    return wrapper