from django.shortcuts import render,redirect
from django.http import JsonResponse, HttpResponse
import datetime
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from AdminPanel.models import UserProfile, Instructor,Branch, Slot, Cource, Student, Attendance, Complain, CourceContent,DLInfo
from django.contrib.auth.models import User
from utils.response import success_response, error_response,validation_error_response

# Create your views here.
def getStudentProfileData(request):
    if request.method == 'GET':
        try:
            student = Student.objects.filter(user__user=request.user).first()
            if not student:
                return error_response(message='Not Allowed',)
            student_data = {
               "id":student.id,
                "name":student.user.user.first_name,
                'profilePic': student.user.profilePic.url if student.user.profilePic else None,
            }
            return success_response(data=student_data)
        except Exception as e:
            return error_response(message=str(e))

@login_required(login_url='signin/')
@csrf_exempt
def change_password(request):
    if request.method == 'POST':
        try:

            if request.user.is_anonymous:
                return error_response(message="User is not authenticated", status=401)
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            

            if not request.user.check_password(current_password):
                return error_response(message="Current password is incorrect", status=400)

            request.user.set_password(new_password)
            request.user.save()
            return success_response(message="Password changed successfully")
        except Exception as e:
            return error_response(message=str(e))

    return  error_response(message="Invalid request method", status=405)
@csrf_exempt
def student_signin(request):
    if request.method == 'POST':
        mobile = request.POST.get('username')  # Use 'username' field for mobile input
        password = request.POST.get('password')
        next_url = request.POST.get('next') or request.GET.get('next') or 'index/'
        print(next_url)
        # Find user by mobile number
        user_profile = UserProfile.objects.filter(phoneNo=mobile).first()
        if not user_profile:
            return render(request, 'student/signin.html', {'error': 'Invalid mobile number or password', 'next': next_url})
        student = Student.objects.filter(user=user_profile).first()
        if not student:
            return render(request, 'student/signin.html', {'error': 'You are not authorized to access this page.', 'next': next_url})
        # Compare password with DOB in ddmmyyyy format
        dob_str = student.dob.strftime('%d%m%Y') if student.dob else ''
        user = authenticate(username=mobile, password=password)
        if not user:
            return render(request, 'student/signin.html', {'error': 'Invalid mobile number or password', 'next': next_url})
        login(request, user_profile.user)
        return redirect(next_url)
    # Pass 'next' to the template if present
    next_url = request.GET.get('next', '')
    return render(request, 'student/signin.html', {'next': next_url})
    


@login_required(login_url='student_signin/')
def getCourseContentData(request):
    if request.method == 'GET':
        try:

            student = Student.objects.filter(user__user=request.user).first()
            if not student:
                return error_response(message='Not Allowed',)
            course_contents = CourceContent.objects.filter(cource=student.cource).order_by('id')
            content_list = []
            for content in course_contents:
                content_list.append({
                    'id': content.id,
                    'title': content.title,
                    'description': content.description,
                    'videoUrl': content.videoUrl,
                    'documentUrl': content.documentUrl.url if content.documentUrl else '',
                })
            return success_response(data=content_list)
            
        except Exception as e:
            return error_response(message=str(e))

@login_required(login_url='student_signin/')
def index(request):
    
        student = Student.objects.filter(user__user=request.user).first()
        if not student:
            return error_response(message='Not Allowed')


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
                    "instructorPhone":student.instructor.user.phoneNo,
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
def getAllUserData(request):
    try:
        users = Instructor.objects.all()
        student  = Student.objects.filter(user__user=request.user).first()
        for user in users:
            if user.instructorBranch == student.Branch:
                user_list = []
                user_list.append({
                    'id': user.id,
                    'name': user.user.user.first_name,
                    'email': user.user.user.email,
                    'phone': user.user.phoneNo,
                    'profilePic': user.user.profilePic.url if user.user.profilePic else '',
                })

        return success_response(data=user_list)
    except Exception as e:
        return error_response(message=str(e))

@login_required(login_url='student_signin/')
def get_student_complaints(request):
    complain_id = request.GET.get('complainId',None)


    try:
        if complain_id:
            complain = Complain.objects.filter(id=complain_id).first()
            if not complain:
                return error_response(message='Complain Not Found')
            complain_data = {
                'id': complain.id,
                'title': complain.compalainTitle,
                'description': complain.compalainFor.user.first_name if complain.compalainFor else '',
                'date': complain.created_at.strftime('%d/%m/%Y'),
                'status': complain.complainResolved,
                'actionTaken': complain.action_taken,
                'resolvedBy': complain.resolved_by.user.first_name if complain.resolved_by else None,
                'resolvedDate': complain.resolved_at.strftime('%d/%m/%Y') if complain.resolved_at else None,
            }
            return success_response(data=complain_data)
        
        student = Student.objects.filter(user__user=request.user).first()
        if not student:
            return error_response(message='Not Allowed')
        
        complain = Complain.objects.filter(compalainForm=student)
        print("Complain Data:", complain)
        complain_list = []
        for comp in complain:
            complain_list.append({
                'id': comp.id,
                'title': comp.compalainTitle,
                'compalainFor': comp.compalainFor.user.first_name if comp.compalainFor else '',
                'date': comp.created_at.strftime('%d/%m/%Y'),
                'status': comp.complainResolved,
            })
        return success_response(data=complain_list)        
    except Exception as e:
        return error_response(message=str(e))


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
            'timeIn': record.timeIn if record.timeIn else None,
            'timeOut': record.timeOut if record.timeOut else None,
            'totalTime': int(diff.total_seconds() / 60) if diff else None,
            
            # 'timeIn': record.timeIn.strftime('%H:%M') if record.timeIn else 'N/A',
            # 'timeOut': record.timeOut.strftime('%H:%M') if record.timeOut else 'N/A',
            'status': 'Present' if record.status == 'Present' else 'Absent'
        })
    return render(request, 'student/manage-attendance.html', {'attendance_data': attendance_data})

@csrf_exempt
def scan_qr(request):

    if request.method == 'POST':
        try:
            student = Student.objects.get(user__user=request.user)
            print("Curretn Student",student)
            qr_code = request.POST.get('qr_code')
            print("Studnet inside",qr_code)
            print("Student QR", student.cource.vehicle.qrCodeData)

            if student.cource.vehicle.qrCodeData == qr_code:
                attendance = Attendance.objects.filter(student=student, date=datetime.now().date()).first()
                if attendance:
                    if attendance.timeOut is None:
                        attendance.timeOut = datetime.now().time()
                        attendance.created_by = student.user
                        attendance.status = 'Present'
                        attendance.save()

                        diff = datetime.combine(datetime.now().date(), attendance.timeOut) - datetime.combine(datetime.now().date(), attendance.timeIn)
                        total_minutes = int(diff.total_seconds() / 60)
                        if total_minutes >=30 and total_minutes <= 45:
                            student.attened_session = int(student.attened_session) + 1
                            student.save()
                        elif total_minutes > 45 and total_minutes <= 60:
                            student.attened_session = int(student.attened_session) + 2
                            student.save()
                        elif total_minutes > 60 and total_minutes <= 75:
                            student.attened_session = int(student.attened_session) + 3
                            student.save()
                        elif total_minutes > 75 and total_minutes <= 90:
                            student.attened_session = int(student.attened_session) + 4
                            student.save()
                        elif total_minutes > 90 and total_minutes <= 120:
                            student.attened_session = int(student.attened_session) + 5
                            student.save()
                        student.save()
                    else:
                        return JsonResponse({'status': 'error', 'message': 'Out Time Already Noted.'})
                    return JsonResponse({'status': 'success', 'message': 'Out Time Noted successfully.'})
                else:
                    Attendance.objects.create(student=student, date=datetime.now().date(), timeIn=datetime.now().time(), status='Present')
                    return JsonResponse({'status': 'success', 'message': 'In Time Noted successfully.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'QR code is invalid.'})
        except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})

@login_required(login_url='student_signin/')
def student_signout(request):
    logout(request)
    return redirect('student_signin/')
