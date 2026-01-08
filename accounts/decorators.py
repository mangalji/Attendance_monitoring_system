from django.shortcuts import redirect
from django.contrib import messages

# def manager_required(view_func):
#     def wrapper(request, *args, **kwargs):
#         if request.user.is_superuser:
#             return view_func(request, *args, **kwargs)

#         if request.user.role == 'manager':
#             return view_func(request, *args, **kwargs)

#         messages.error(request, "Access denied")
#         return redirect('login')
#     return wrapper


# def student_required(view_func):
#     def wrapper(request, *args, **kwargs):
#         if request.user.role == 'student':
#             return view_func(request, *args, **kwargs)

#         messages.error(request, "Access denied")
#         return redirect('login')
#     return wrapper

def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper(request,*args,**kwargs):
            if request.user.is_superuser:
                return view_func(request,*args,**kwargs)
            if request.user.role in allowed_roles:
                return view_func(request,*args,**kwargs)
            messages.error(request,"Access Denied")
            return redirect('login')
        return wrapper
    return decorator

student_required = role_required(['student'])
manager_required = role_required(['manager'])