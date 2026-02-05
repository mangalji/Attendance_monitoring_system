from django.contrib import admin

from .models import Manager, Student, Parent, Placement,Company, User
from .forms import ManagerCreationForm, CustomUserCreationForm, StudentAdminCreationForm
from django.contrib.auth.admin import UserAdmin

# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserCreationForm
#     model = User
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'password1', 'password2'),
#         }),
#     )
#     list_display = ['username','email','is_staff','is_active']
#
# admin.site.register(User,CustomUserAdmin) 


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('id','user','phone')

    def get_form(self,request,obj=None,**kwargs):
        if obj is None:
            return ManagerCreationForm
        return super().get_form(request,obj,**kwargs)
    

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentAdminCreationForm
    list_display = ('roll_no','user_email','domain','joining_date','is_placed','is_active')
    list_filter = ('domain','is_placed','is_active')
    search_fields = ('roll_no','user__email')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def save_model(self, request, obj, form, change):
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        
        if not change:
            # Creating new student -> create new user
            user = User.objects.create_user(username=email, email=email, password=password)
            obj.user = user
        else:
            # Updating existing student -> update user email
            user = obj.user
            user.email = email
            user.username = email
            if password:
                user.set_password(password)
            user.save()
            
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
             # Populate email field when editing
             form.base_fields['email'].initial = obj.user.email
        return form

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('student','name','relation','phone')

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'job_location')


@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    list_display = ('student', 'company', 'placed_date')

