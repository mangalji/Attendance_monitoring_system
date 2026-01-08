from django.contrib import admin
from .models import CustomUser, Student, Manager, Parent, Domain, Company, Placement

admin.site.register(CustomUser)
admin.site.register(Student)
admin.site.register(Manager)
admin.site.register(Parent)
admin.site.register(Domain)
admin.site.register(Company)
admin.site.register(Placement)
