from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import datetime
from AdminPanel.models import UserProfile, Branch, Slot, Cource, Student, Attendance, Complain, CourceContent,DLInfo,Instructor
# Create your views here.

def instructor_signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next') or request.GET.get('next') or 'index/'
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'instructor/signin.html', {'error': 'Invalid username or password'})
        user_profile = UserProfile.objects.filter(user=user).first()
        instructor = Instructor.objects.filter(user=user_profile).first()
        if not instructor:
            return render(request, 'instructor/signin.html', {'error': 'You are not authorized to access this page.'})
        else:
            login(request, user)
            return redirect(next_url)
    next_url = request.GET.get('next', '')
    return render(request, 'instructor/signin.html', {'next': next_url})


@login_required(login_url='instructor_signin/')
def getIndexData(request):
    studentId = request.GET.get('studentId',None)
    if studentId:
        try:
            instuctor = Instructor.objects.filter(user__user=request.user).first()
            student = Student.objects.get(id=studentId,instructor=instuctor)
            if not student:
                return JsonResponse({"error":"Student not found"},status=404)
            studentData = {
                "id":student.id,
                "name":student.user.user.first_name,
                "cource":student.cource.courceName,
                "phone":student.user.phoneNo,
                "slot":f"{student.slot.slotStart}-{student.slot.slotEnd}",
            }
            return JsonResponse(studentData,safe=False)
        except Exception as e:
            return JsonResponse({"error":"Student not found"},status=404)   
    instuctor = Instructor.objects.filter(user__user=request.user).first()
    studentList = Student.objects.filter(instructor = instuctor)
    todayDate = datetime.date.today()
    attendanceTaken = Attendance.objects.filter(student__in=studentList,date=todayDate).exists()
    studentList = [{"id":s.id,"name":s.user.user.first_name,
                    "cource":s.cource.courceName,
                    "phone":s.user.phoneNo,"slot":f"{s.slot.slotStart}-{s.slot.slotEnd} ",
                    "attendanceTaken": Attendance.objects.filter(student=s,date=todayDate).exists()} for s in studentList]
    return JsonResponse(studentList, safe=False)
@login_required(login_url='instructor_signin/')
def getReamainingPaymentData(request):
    studentId = request.GET.get('studentId',None)
    if studentId:
        try:
            student = Student.objects.get(id=studentId)
            if not student:
                return JsonResponse({"error":"Student not found"},status=404)
            studentData = {
                "id":student.id,
                "name":student.user.user.first_name,
                "cource":student.cource.courceName,
                "phone":student.user.phoneNo,
                "slot":f"{student.slot.slotStart}-{student.slot.slotEnd}",
                "paid":student.paymentRecieved,
                "pending":student.paymentPending,
                "dueDate":student.paymentDueDate
            }
            return JsonResponse(studentData,safe=False)
        except Exception as e:
            return JsonResponse({"error":"Student not found"},status=404)
    instuctor = Instructor.objects.filter(user__user=request.user).first()
    studentList = Student.objects.filter(instructor = instuctor)
    studentList = [{"id":s.id,"name":s.user.user.first_name,
                    "cource":s.cource.courceName,
                    "phone":s.user.phoneNo,"slot":f"{s.slot.slotStart}-{s.slot.slotEnd} ",
                    "paid":s.amountPaid,
                    "pending":s.amountPending,
                    "dueDate":s.paymentDueDate} for s in studentList if s.amountPending > 0]
    return JsonResponse(studentList, safe=False)
@login_required(login_url='instructor_signin/')
def index(request):
    # ins =Instructor.objects.filter(user=request.user).first()

    return render(request, 'instructor/index.html')


@login_required(login_url='instructor_signin/')
def takeAttendance(request):
    if request.method == 'POST':
        student = request.POST.get('studentName')
        date = request.POST.get('attendanceDate')
        inTime = request.POST.get('inTime')
        outTime = request.POST.get('outTime')
        status = request.POST.get('attendanceStatus')
        try:
            attendance = Attendance(student=Student.objects.get(id=student),date=date,timeIn=inTime,timeOut=outTime,status=status)
            attendance.save()
            return JsonResponse({'success': 'Attendance added successfully'})
        except Exception as e:
            if "UNIQUE constraint failed" in str(e): #check for unique constraint violation.
                return JsonResponse({'error': 'Attendance already Added'}, status=400)
            return JsonResponse({'error': 'Attendance not added'}, status=404)
    else:
        return JsonResponse({"status":"failed"})

@login_required(login_url='instructor_signin/')
def signout(request):
    logout(request)
    return redirect('instructor_signin/')