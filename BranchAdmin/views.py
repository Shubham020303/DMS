from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from AdminPanel.models import (
    DLInfo, Instructor, Vehicle, Cource, Student, Attendance, Branch,
    UserProfile, Complain, CourceContent, Slot, Payment, AddOnService, Notification
)
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt

@login_required(login_url='/branchadmin/signin/')
def index(request):
    return render(request, 'BranchAdmin/index.html')

def get_branch(request):
    # Helper to get branch for current branch admin
    user_profile = UserProfile.objects.get(user=request.user)
    return user_profile.branchadmin_branch_set.first() if hasattr(user_profile, 'branchadmin_branch_set') else Branch.objects.filter(branchIncharge=user_profile).first()

@login_required(login_url='/branchadmin/signin/')
def getStudentData(request):
    branch = get_branch(request)
    students = Student.objects.filter(Branch=branch)
    data = []
    for student in students:
        data.append({
            'id': student.id,
            'name': student.user.user.first_name,
            'email': student.user.user.email,
            'phone': student.user.phoneNo,
            'applicationNo': student.applicationNo,
            'dob': student.dob,
            'address': student.address,
            'branch': student.Branch.branchName,
            'bloodGroup': student.user.bloodGroup,
            'profilePic': student.user.profilePic.url if student.user.profilePic else None,
            'gender': student.gender,
            "bookingType": student.booking_Type,
            'cource': student.cource.courceName,
            'instructor': student.instructor.user.user.first_name,
            'startDate': student.courceEnrollDate,
            'endDate': student.courceEndDate,
            'status': "Active" if student.student_staus else "Inactive",
            'addOnService': [addOnService.serviceName for addOnService in student.addOnService.all()],
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
@login_required(login_url='/branchadmin/signin/')
def manage_student(request):
    branch = get_branch(request)
    if request.method == 'POST':
        id = request.POST.get('studentId')
        name = request.POST.get('studentName')
        email = request.POST.get('studentEmail')
        dob = request.POST.get('dob')
        applicationNo = request.POST.get('applicationNo')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        bloodGroup = request.POST.get('bloodGroup')
        profilepic = request.FILES.get('profilePic',None)
        gender = request.POST.get('studentGender')
        dlNo = request.POST.get('dlNo',None)
        dlIssueDate = request.POST.get('dlIssueDate',None)
        dlExpiry = request.POST.get('dlExpiry',None)
        dlType = request.POST.get('dlType',None)
        cource = request.POST.get('studentCourse')
        instructor = request.POST.get('studentInstructor')
        bookingType = request.POST.get('bookingType')
        slot = request.POST.get('studentSlot')
        startDate = request.POST.get('courseStartDate')
        endDate = request.POST.get('courseEndDate')
        paymentRecieved = request.POST.get('paymentReceived')
        paymentDue = request.POST.get('paymentDue')
        paymentDueDate = request.POST.get('paymentDueDate',None)
        addOnService = request.POST.get('addOnService',None)
        paymentRecievedBy = request.POST.get('paymentRecievedBy')
        if addOnService:
            addOnService = map(int, addOnService.split(','))
            addOnService = list(addOnService)
        try:
            if Student.objects.filter(id=id, Branch=branch).exists():
                student = Student.objects.get(id=id, Branch=branch)
                student.user.user.first_name = name
                student.user.user.email = email
                student.user.user.username = email
                student.user.user.save()
                student.user.phoneNo = phone
                student.user.bloodGroup = bloodGroup
                if profilepic:
                    student.user.profilePic = profilepic
                student.user.save()
                dlinfo = DLInfo.objects.filter(dlUser=student.user).first()
                if dlinfo:
                    dlinfo.dlType = dlType
                    dlinfo.dlNo = dlNo
                    dlinfo.dlIssueDate = dlIssueDate
                    dlinfo.dlExpiry = dlExpiry
                    dlinfo.save()
                else:
                    if dlNo:
                        dlinfo = DLInfo(dlUser=student.user,dlType=dlType,dlNo=dlNo,dlIssueDate=dlIssueDate,dlExpiry=dlExpiry)
                        dlinfo.save()
                student.cource = Cource.objects.get(id=cource, Branch=branch)
                student.instructor = Instructor.objects.get(user_id=instructor, instructorBranch=branch)
                student.Branch = branch
                student.slot = Slot.objects.get(id=slot, slotBranch=branch)
                if bookingType == 'Pre-Booking':
                    student.slot.slotPreBooked = True
                    student.slot.save()
                else:
                    student.slot.slotPreBooked = False
                    student.slot.save()
                student.dob = dob
                student.address = address
                student.applicationNo = applicationNo
                student.gender = gender
                student.courceEnrollDate = startDate
                student.courceEndDate = endDate
                student.amountPaid = paymentRecieved
                student.amountPending = paymentDue
                student.paymentDueDate = paymentDueDate
                student.addOnService.clear()
                for addOnServiceId in addOnService:
                    student.addOnService.add(AddOnService.objects.get(id=addOnServiceId))
                student.save()
                return JsonResponse({'status': 'success'})
            else:
                newuser = None
                userprofile = None
                Dlinfo = None
                try:
                    if UserProfile.objects.filter(phoneNo=phone).exists():
                        newuser = UserProfile.objects.get(phoneNo=phone).user
                    else:
                        newuser = User.objects.create_user(username=phone, password=dob, first_name=name)
                    userprofile = UserProfile(user=newuser, phoneNo=phone, is_student=True, profilePic=profilepic ,bloodGroup=bloodGroup)
                    userprofile.save()
                    cource_obj = Cource.objects.get(id=cource, Branch=branch)
                    instructor_obj = Instructor.objects.get(user__id=instructor, instructorBranch=branch)
                    slot_obj = Slot.objects.get(id=slot, slotBranch=branch)
                    if bookingType == 'Pre-Booking':
                        slot_obj.slotPreBooked = True
                        slot_obj.save()
                    else:
                        slot_obj.slotPreBooked = False
                        slot_obj.slotUsed = True
                        slot_obj.save()
                    if paymentDueDate == "":
                        paymentDueDate = None
                    student = Student(user=userprofile, applicationNo=applicationNo, dob=dob, address=address,Branch=branch,gender=gender, cource=cource_obj, instructor=instructor_obj, slot=slot_obj,courceEnrollDate=startDate,courceEndDate = endDate,amountPaid=paymentRecieved,amountPending=paymentDue,paymentDueDate=paymentDueDate,booking_Type=bookingType)
                    payment = Payment(student=student,paymentDate=datetime.today().date(),paymentAmount=paymentRecieved,paymentMethod='Cash',paymentRecevedBy=UserProfile.objects.get(id=paymentRecievedBy))
                    student.save()
                    addontoatal = 0
                    if addOnService:
                        for addOn in addOnService:
                            addOnServiceObj = AddOnService.objects.get(id=addOn)
                            student.addOnService.add(addOnServiceObj)
                            addontoatal += int(addOnServiceObj.serviceFee)
                    student.save()
                    payment.save()
                    if dlNo:
                        dlinfo = DLInfo.objects.create(dlNo=dlNo, dlIssueDate=dlIssueDate, dlExpiry=dlExpiry, dlUser=userprofile,dlType=dlType)
                        dlinfo.save()
                except Exception as e:
                    if newuser:
                        newuser.delete()
                        slot_obj.slotPreBooked = False
                        slot_obj.slotUsed = False
                        slot_obj.save()
                    return JsonResponse({'status': 'error', 'message': str(e)})
                return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    if request.method == 'DELETE':
        try:
            id = request.GET.get('studentId')
            student = Student.objects.get(id=id, Branch=branch)
            student.slot.slotPreBooked = False
            student.slot.slotUsed = False
            student.slot.save()
            userProf = UserProfile.objects.get(id=student.user.id)
            user = User.objects.get(id=userProf.user.id)
            userProf.delete()
            student.delete()
            user.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return render(request, 'BranchAdmin/manage-student.html')

@login_required(login_url='/branchadmin/signin/')
def getInstructorData(request):
    branch = get_branch(request)
    instructors = Instructor.objects.filter(instructorBranch=branch)
    data = []
    for instructor in instructors:
        data.append({
            'id': instructor.user.id,
            'name': instructor.user.user.first_name,
            'email': instructor.user.user.email,
            'phone': instructor.user.phoneNo,
            'branch': instructor.instructorBranch.branchName,
            'vehicle': instructor.instructorVehicle.vehicleName if instructor.instructorVehicle else '',
            'bloodGroup': instructor.user.bloodGroup,
            'profilePic': instructor.user.profilePic.url if instructor.user.profilePic else '',
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
@login_required(login_url='/branchadmin/signin/')
def manage_instructor(request):
    branch = get_branch(request)
    # Only allow CRUD for instructors in this branch
    # ...implement POST, DELETE, and GET logic as in AdminPanel, but always use instructorBranch=branch...
    # ...existing code...
    return render(request, 'BranchAdmin/manage-instructor.html')

@login_required(login_url='/branchadmin/signin/')
def getVehicleData(request):
    branch = get_branch(request)
    vehicles = Vehicle.objects.filter(vehicleBranch=branch)
    vehicalData = []
    for i in vehicles:
        vehicalData.append({
            'id': i.id,
            'vehicalName': i.vehicleName,
            'vehicleNo': i.vehicleNo,
            'vehicleType': i.vehicleType,
            'insuranceValidity': i.insuranceValidity.strftime('%Y-%m-%d'),
            'pollutionValidity': i.pollutionValidity.strftime('%Y-%m-%d'),
            'fitnessValidity': i.fitnessValidity.strftime('%Y-%m-%d'),
        })
    return JsonResponse(vehicalData, safe=False)

@csrf_exempt
@login_required(login_url='/branchadmin/signin/')
def manage_vehicle(request):
    branch = get_branch(request)
    # Only allow CRUD for vehicles in this branch
    # ...implement POST, DELETE, and GET logic as in AdminPanel, but always use vehicleBranch=branch...
    # ...existing code...
    return render(request, 'BranchAdmin/manage-vehicle.html')

@login_required(login_url='/branchadmin/signin/')
def getCourseData(request):
    branch = get_branch(request)
    courses = Cource.objects.filter(Branch=branch)
    courseData = []
    for i in courses:
        courseData.append({
            'id': i.id,
            'courseName': i.courceName,
            'courseDuration': i.courceDuration,
            'courseFee': i.courceFee,
            'courceVehicle': i.vehicle.vehicleName if hasattr(i, 'vehicle') and i.vehicle else '',
            'courseBranch': i.Branch.branchName
        })
    return JsonResponse(courseData, safe=False)

@csrf_exempt
@login_required(login_url='/branchadmin/signin/')
def manage_course(request):
    branch = get_branch(request)
    # Only allow CRUD for courses in this branch
    # ...implement POST, DELETE, and GET logic as in AdminPanel, but always use Branch=branch...
    # ...existing code...
    return render(request, 'BranchAdmin/manage-course.html')

@login_required(login_url='/branchadmin/signin/')
def getAttendanceData(request):
    branch = get_branch(request)
    students = Student.objects.filter(Branch=branch)
    attendance = Attendance.objects.filter(student__in=students)
    attendanceData = []
    for i in attendance:
        attendanceData.append({
            'id': i.id,
            'student': i.student.user.user.first_name,
            'studentId': i.student.id,
            'date': i.date,
            'timeIn': i.timeIn,
            'timeOut': i.timeOut,
            'status': i.status,
        })
    return JsonResponse(attendanceData, safe=False)

@csrf_exempt
@login_required(login_url='/branchadmin/signin/')
def manageAttendance(request):
    branch = get_branch(request)
    # Only allow CRUD for attendance of students in this branch
    # ...implement POST, DELETE, and GET logic as in AdminPanel, but always use students from this branch...
    # ...existing code...
    return render(request, 'BranchAdmin/manage-attendance.html')

@login_required(login_url='/branchadmin/signin/')
def getAddOnServiceData(request):
    # AddOnService is global, so just return all
    addOnServices = AddOnService.objects.all()
    addOnServiceData = []
    for i in addOnServices:
        addOnServiceData.append({
            'id': i.id,
            'addOnServiceName': i.serviceName,
            'addOnServiceAmount': i.serviceFee,
            'mandetory': i.mandetory,
        })
    return JsonResponse(addOnServiceData, safe=False)

@csrf_exempt
@login_required(login_url='/branchadmin/signin/')
def manageAddOnService(request):
    # Only allow update/delete, not create (if you want to restrict creation)
    # ...existing code...
    return render(request, 'BranchAdmin/manage-addonservice.html')

@login_required(login_url='/branchadmin/signin/')
def getNotificationData(request):
    branch = get_branch(request)
    notifications = Notification.objects.filter(notificationBranch=branch)
    notificationData = []
    for i in notifications:
        if not i.notificationIsRead:
            notificationData.append({
                'id': i.id,
                'notificationTitle': i.notificationTitle,
                'notificationTime': i.notificationTime.strftime("%I:%M %p"),
                'notificationDate': i.notificationDate.strftime("%Y-%m-%d"),
                'notificationBranch': i.notificationBranch.branchName,
            })
    return JsonResponse(notificationData, safe=False)

@csrf_exempt
@login_required(login_url='/branchadmin/signin/')
def manageNotification(request):
    branch = get_branch(request)
    # Only allow update/delete for notifications in this branch
    # ...existing code...
    return render(request, 'BranchAdmin/manage-notification.html')

# Branch admin cannot create new branches, so do not implement manage_branch or similar view.

# You will need to create templates:
# BranchAdmin/index.html
# BranchAdmin/manage-student.html
# BranchAdmin/manage-instructor.html
# BranchAdmin/manage-vehicle.html
# BranchAdmin/manage-course.html
# BranchAdmin/manage-attendance.html
# BranchAdmin/manage-addonservice.html
# BranchAdmin/manage-notification.html



