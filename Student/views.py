from django.shortcuts import render,redirect
from django.http import JsonResponse, HttpResponse
import datetime
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from AdminPanel.models import UserProfile, Branch, Slot, Cource, Student, Attendance, Complain, CourceContent,DLInfo
# Create your views here.
def student_signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next') or request.GET.get('next') or 'index/'
        print(next_url)
        user = authenticate(username=username, password=password)
        print(user)
        # Check if user is not None and is a student
        if user is None:
            return render(request, 'student/signin.html', {'error': 'Invalid username or password'})
        # If user is authenticated, check if they are a student
        user_profile = UserProfile.objects.filter(user=user).first()
        student = Student.objects.filter(user=user_profile).first()

        if not student:
            return render(request, 'student/signin.html', {'error': 'You are not authorized to access this page.'})
        else:
            login(request, user)
            return redirect(next_url)
        
    # Pass 'next' to the template if present
    next_url = request.GET.get('next', '')
    return render(request, 'student/signin.html', {'next': next_url})

@login_required(login_url='student_signin/')
def index(request):
    student = Student.objects.get(user__user=request.user)
    dlinfo = DLInfo.objects.filter(dlUser=student.user).first()
   
    studentData = {
                "id":student.id,
                "name":student.user.user.first_name,
                "DOB":student.dob.strftime('%d/%m/%Y') if student.courceEnrollDate else '',
                "address":student.address,
                "Profilepic":student.user.profilePic.url if student.user.profilePic else '',
                "course":student.cource.courceName,
                "enrollmentDate":student.courceEnrollDate.strftime('%d/%m/%Y') if student.courceEnrollDate else '',
                "completionDate":student.courceEndDate.strftime('%d/%m/%Y') if student.courceEnrollDate else '',
                "vehicle":student.cource.vehicle.vehicleName if student.cource.vehicle.vehicleName else '',
                "instructor":student.instructor.user.user.first_name,
                "dueamount":student.amountPending if student.amountPending > 0 else None,
                "dueDate":student.paymentDueDate.strftime('%d/%m/%Y') if student.paymentDueDate else '',
                "phone":student.user.phoneNo,
                "DlNo":dlinfo.dlNo if dlinfo and dlinfo.dlNo else None,
                "DlIssueDate":dlinfo.dlIssueDate.strftime('%d/%m/%Y') if dlinfo and dlinfo.dlIssueDate else None,
                "DlExpiry":dlinfo.dlExpiry.strftime('%d/%m/%Y') if dlinfo and dlinfo.dlExpiry else None,
                "DlType":dlinfo.dlType if dlinfo and dlinfo.dlType else None

            }
    
    return render(request, 'student/index.html',context=studentData)

@login_required(login_url='student_signin/')
def manage_complaints(request):
    return render(request, 'student/student-complains.html')

@login_required(login_url='student_signin/')
def manage_course(request):
    return render(request, 'student/course-details.html')




@login_required(login_url='student_signin/')
def manage_attendance(request):
    student = Student.objects.get(user__user=request.user)
    attendance_records = Attendance.objects.filter(student=student).order_by('-date')
    print(attendance_records)
    attendance_data = []
    for record in attendance_records:
        time1 = record.timeIn
        time2 = record.timeOut
        date = record.date
        if time1 and time2:
            date1 = datetime.combine(date, time1)
            date2 = datetime.combine(date, time2)
            diff = date2 - date1
        else:
            diff = None  
        attendance_data.append({
            'date': record.date.strftime('%d/%m/%Y'),
            'date': record.date,
            'timeIn': record.timeIn,
            'timeOut': record.timeOut,
            'totalTime': int(diff.total_seconds() / 60) if diff else None,
            
            # 'timeIn': record.timeIn.strftime('%H:%M') if record.timeIn else 'N/A',
            # 'timeOut': record.timeOut.strftime('%H:%M') if record.timeOut else 'N/A',
            'status': 'Present' if record.status else 'Absent'
        })
    return render(request, 'student/manage-attendance.html', {'attendance_data': attendance_data})

@csrf_exempt
def scan_qr(request):

    if request.method == 'POST':
        student = Student.objects.get(user__user=request.user)
        qr_code = request.POST.get('qr_code')

        if student.cource.vehicle.qrCodeData == qr_code:
            attendance = Attendance.objects.filter(student=student, date=datetime.now().date()).first()
            if attendance:
                if attendance.timeOut is None:
                    attendance.timeOut = datetime.now().time()
                    attendance.save()
                    student.attened_session = int(student.attened_session) + 1
                    student.save()
                else:
                    return JsonResponse({'status': 'error', 'message': 'Out Time Already Noted.'})
                return JsonResponse({'status': 'success', 'message': 'Out Time Noted successfully.'})
            else:
                Attendance.objects.create(student=student, date=datetime.now().date(), timeIn=datetime.now().time(), status='Present')
                return JsonResponse({'status': 'success', 'message': 'In Time Noted successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'QR code is invalid.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@login_required(login_url='student_signin/')
def signout(request):
    logout(request)
    return redirect('student_signin/')
