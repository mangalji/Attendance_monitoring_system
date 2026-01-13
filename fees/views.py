from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import manager_required, student_required
from accounts.models import StudentProfile, Notification
from .models import FeeRecord

@login_required
def fee_manager(request):
    if not (request.user.is_superuser or hasattr(request.user, 'managerprofile')):
        return redirect('student_dashboard')
    
    students = list(StudentProfile.objects.select_related('fee_record', 'user').all())
    

    def studnet_sorting(s):
        try:
            return int(s.roll_no)
        except ValueError:
            return s.roll_no

    students.sort(key=studnet_sorting)
    
    # Ensure every student has a FeeRecord 
    for student in students:
        if not hasattr(student, 'fee_record'):
            FeeRecord.objects.get_or_create(student=student)
            
    return render(request, 'fees/fee_manager.html', {'students': students})

@login_required
def update_fee(request, student_id):
    if not (request.user.is_superuser or hasattr(request.user,'managerprofile')):
        return redirect('student_dashboard')

    if request.method == 'POST':
        try:
            student = StudentProfile.objects.get(id=student_id)
            fee_record, created = FeeRecord.objects.get_or_create(student=student)
            
            
            fee_record.total_fees = float(request.POST.get('total_fees', 0) or 0)
            fee_record.paid_fees = float(request.POST.get('paid_fees', 0) or 0)
            
           
            for i in range(1, 5):
                file_key = f'installment_{i}'
                if file_key in request.FILES:

                    setattr(fee_record, file_key, request.FILES[file_key])
            
            fee_record.save()

            Notification.objects.create(
                recipient = student.user,
                message = f"your fees record has been updated. total paid fees: ₹{fee_record.paid_fees}",
                notification_type = 'fees'
            )

            messages.success(request, f"fees and receipts updated for {student.user.first_name}")
        except Exception as e:
            messages.error(request, f"error updating fees: {str(e)}")
        
    return redirect('fee_manager')

@login_required
def send_fee_reminder(request,student_id):
    if not(request.user.is_superuser or hasattr(request.user, 'managerprofile')):
        return redirect('student_dashboard')
    
    student = get_object_or_404(StudentProfile,id=student_id)
    Notification.objects.create(
        recipient = student.user,
        message = "reminder! plese pay your pending fees as soon as possible.",
        notification_type = 'reminder'
    )
    messages.success(request,f"fee reminder sent to {student.user.first_name}")
    return redirect('fee_manager')

def student_view_fees(request):
    try:
        student = request.user.studentprofile

    except StudentProfile.DoesNotExist:
        messages.error(request,'student profile not found')
        return redirect('student_dashboard')
    
    fee_record, created = FeeRecord.objects.get_or_create(student=student) 
    return render(request,'fees/student_view_fees.html',{'fee_record':fee_record})
