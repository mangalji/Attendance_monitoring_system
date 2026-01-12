from django.urls import path
from . import views

urlpatterns = [
    path('manager/fee-manager/', views.fee_manager, name='fee_manager'),
    path('manager/update-fee/<int:student_id>/', views.update_fee, name='update_fee'),
    path('manager/view-fees/',views.student_view_fees,name='student_view_fees'),
]
