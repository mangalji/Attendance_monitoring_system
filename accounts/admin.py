from django.contrib import admin

# Register your models here.
from .models import ManagerProfile, StudentProfile, Parent, Placement,Company
from .forms import ManagerCretionForm

@admin.register(ManagerProfile)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('id','user','phone')

    def get_form(self,request,obj=None,**kwargs):
        if obj is None:
            return ManagerCretionForm
        return super().get_form(request,obj,**kwargs)
    

@admin.register(StudentProfile)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_no','user','domain','joining_date','is_placed','is_active')
    list_filter = ('domain','is_placed','is_active')
    search_fields = ('roll_no','user__first_name','user__email')

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('student','name','relation','phone')
