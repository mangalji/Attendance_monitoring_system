from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import manager_required
from accounts.models import StudentProfile
from .models import FeeRecord

@login_required
@manager_required
def fee_manager(request):
    # Fetch all students and their fee records
    students = list(StudentProfile.objects.select_related('fee_record', 'user').all())
    
    # Natural sort logic (1, 2, 3 instead of 1, 10, 2)
    def natural_sort_key(s):
        try:
            return int(s.roll_no)
        except ValueError:
            return s.roll_no

    students.sort(key=natural_sort_key)
    
    # Ensure every student has a FeeRecord 
    for student in students:
        if not hasattr(student, 'fee_record'):
            FeeRecord.objects.get_or_create(student=student)
            
    return render(request, 'fees/fee_manager.html', {'students': students})

@login_required
@manager_required
def update_fee(request, student_id):
    if request.method == 'POST':
        try:
            student = StudentProfile.objects.get(id=student_id)
            fee_record, created = FeeRecord.objects.get_or_create(student=student)
            
            # Update numeric fields
            fee_record.total_fees = float(request.POST.get('total_fees', 0) or 0)
            fee_record.paid_fees = float(request.POST.get('paid_fees', 0) or 0)
            
            # Receipts (Files)
            for i in range(1, 5):
                file_key = f'installment_{i}'
                if file_key in request.FILES:
                    # If a new file is uploaded, set it. Django handles storage.
                    setattr(fee_record, file_key, request.FILES[file_key])
            
            fee_record.save()
            messages.success(request, f"Fees and receipts updated for {student.user.first_name}")
        except Exception as e:
            messages.error(request, f"Error updating fees: {str(e)}")
        
    return redirect('fee_manager')
