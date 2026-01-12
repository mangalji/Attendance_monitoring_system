from django.contrib import admin

# Register your models here.
from .models import ManagerProfile, StudentProfile, Parent, Placement,Company
from .forms import ManagerCreationForm

@admin.register(ManagerProfile)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('id','user','phone')

    def get_form(self,request,obj=None,**kwargs):
        if obj is None:
            return ManagerCreationForm
        return super().get_form(request,obj,**kwargs)
    

@admin.register(StudentProfile)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_no','user','domain','joining_date','is_placed','is_active')
    list_filter = ('domain','is_placed','is_active')
    search_fields = ('roll_no','user__first_name','user__email')

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('student','name','relation','phone')

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'job_location')


@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    list_display = ('student', 'company', 'placed_date')
