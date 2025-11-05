from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from datetime import datetime,timedelta
from .models import (DLInfo,Instructor,Vehicle,Cource,Student,Attendance,Branch,UserProfile,Complain,CourceContent,Slot,Payment,AddOnService,Notification,StudentCouseHistory)
from django.core.paginator import Paginator
from utils.response import success_response, error_response,validation_error_response
import logging
# Create your views here.

logger = logging.getLogger(__name__)

def _parse_date_string(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()

@login_required(login_url='signin/')
def getcurrentUserData(request):
    try:
        if request.user.is_authenticated:
            user = request.user
            user_profile = UserProfile.objects.filter(user=user).first()
            if user_profile:
                data = {
                    'id': user.id,
                    'name': user.first_name,
                    'email': user.email,
                    'phone': user_profile.phoneNo,
                    'profilePic': user_profile.profilePic.url if user_profile.profilePic else '',
                    'is_superAdmin': user_profile.is_superAdmin,
                    'is_instructor': user_profile.is_instructor,
                    'is_branchAdmin': user_profile.is_branchAdmin,
                    'is_student': user_profile.is_student,
                }
                return success_response(data=data, message="Current user data fetched successfully")
            else:
                return error_response(message="User profile not found", status=404)
        else:
            return validation_error_response(message="User is not authenticated", status=401)
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
@login_required(login_url='signin/')
def reset_password(request):
    if request.method == 'POST':
        try:
            userid = request.POST.get('userId',None)
            phone =  request.POST.get('phoneNo')
            dob = request.POST.get('dob')
            dob_obj = datetime.strptime(dob, '%Y-%m-%d')
            dob_str  = dob_obj.strftime('%d%m%Y')

            if userid:
                user = User.objects.filter(id=userid).first()
            else:
                user = User.objects.filter(username = phone).first()
            print(user)
            if not user:
                return error_response(message="User does not exist", status=404)
            # For simplicity, we are resetting the password to 'defaultpassword123'
            user.set_password(dob_str)
            user.save()
            return success_response(message="Password has been reset to 'Default Password'.")
        except Exception as e:
            return error_response(message=str(e))


@login_required(login_url='signin/')
def getReamainingPaymentData(request):
    try:
        studentid= request.GET.get('studentId',None)
        if studentid:
            student = Student.objects.filter(id=studentid).first()
            if not student:
                return error_response(message="Student not found", status=404)
            data = {
                'name': student.user.user.first_name,
                'studentId': student.id,
                'paymentDue': student.amountPending

            }
            return success_response(data=data, message="Remaining payment fetched successfully for a studnet ID")
        else:
            three_days_ago = datetime.today() - timedelta(days=3)
            students = Student.objects.filter(amountPending__gt=0, paymentDueDate__lte=three_days_ago)
            print("Students with pending payments:", students)
            data = []
            for student in students:
                data.append({
                    'name': student.user.user.first_name,
                    'studentId': student.id,
                    'courseName': student.cource.courceName,
                    'amountPending': student.amountPending,
                    'amountPaid': student.amountPaid,
                    'TotalAmount': int(student.amountPending) + int(student.amountPaid),
                    'paymentDueDate': student.paymentDueDate
                })  
            
                        
            return success_response(data=data, message="Remaining payments fetched successfully for all students")
    except Exception as e:
        return error_response(message=str(e))
        
@login_required(login_url='signin/')
def getSlotWiseData(request):
    try:
        date = request.GET.get('date', None)
        today = datetime.today().date()
        if not date:
            date = today
        vehicle = Vehicle.objects.all()  
        data = []
        for i in vehicle:
            if i.is_active == True:
                tempData = {
                    'vehicleName': i.vehicleName,
                    }
                slots = Slot.objects.filter(vehicle=i)
                
                temp_slot_data = []
                for slot in slots:
                    if slot.is_active == True:
                        student = Student.objects.filter(cource__vehicle=i,slot=slot,student_staus=True,booking_Type = 'Normal',courceEndDate__gte=today)
                        if slot.slotPreBooked:
                            prebookstudent = Student.objects.filter(cource__vehicle=i,slot=slot,student_staus=True,booking_Type = 'Pre-Booking',courceEndDate__gte=today).first()

                        if student.exists():
                            attandance = Attendance.objects.filter(student=student.first(),date=date).first()
                        slot_data = {
                            'slotTime': f'{slot.slotStart} - {slot.slotEnd}',
                            'branch': slot.slotBranch.branchName,
                            'student': student.first().user.user.first_name if student.exists() else None,
                            "attendanceStatus": attandance.status if student.exists() and attandance else "NotMarked",
                            "prebookedStudent": prebookstudent.user.user.first_name if slot.slotPreBooked and prebookstudent else None,
                            "prebookStartDate" : prebookstudent.courceEnrollDate if slot.slotPreBooked and prebookstudent else None,
                        }
                        temp_slot_data.append(slot_data)
                    tempData['slots'] = temp_slot_data
                data.append(tempData)
                
        return success_response(data=data, message="slotwise data fetched successfully")
    except Exception as e:
        return error_response(message=str(e))            
@login_required(login_url='signin/')
def getStudentOnLeaveData(request):
    try:
        next_day = datetime.today().date() + timedelta(days=1)
        today =datetime.today().date()
        attendance = Attendance.objects.filter(status='Leave', date__gte=today, date__lte=next_day)
        data = []
        for i in attendance:
            data.append({
                'studentName': i.student.user.user.first_name,
                "slotTime": f'{i.student.slot.slotStart} - {i.student.slot.slotEnd}',
                'date': i.date,
                'status': i.status
            })
        return success_response(data=data, message="Students on leave fetched successfully")
    except Exception as e:
        return error_response(message=str(e))

@login_required(login_url='signin/')  
def getEearningData(request):
    try:
        branches = Branch.objects.all()
        data = []
        for branch in branches:
            students = Student.objects.filter(Branch=branch)
            
            total_amount_paid = 0
            total_amount_remaining = 0
            for student in students:
                total_amount_paid += student.amountPaid
                total_amount_remaining += student.amountPending
            total_earning = total_amount_paid + total_amount_remaining
            data.append({
                'branch': branch.branchName,
                'branchInCharge': branch.branchIncharge.user.first_name,
                'totalEarning': total_earning,
                'totalAmountPaid': total_amount_paid,
                'totalAmountRemaining': total_amount_remaining
            })
        return success_response(data=data, message="Earning data fetched successfully for all branches")
    except Exception as e:
        return error_response(message=str(e))
    
@login_required(login_url='signin/')
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def signin(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            next_url = request.POST.get('next') or request.GET.get('next') or 'index/'
            
            user = authenticate(username=username, password=password)
            if user is not None:
                # Check if the user is a is_superAdmin
                userProf = UserProfile.objects.filter(user=user).first()
                if not userProf.is_superAdmin:
                    return render(request, 'signin.html', {'error': 'You are not authorized to access this page.'})
                else:
                    login(request, user)
                    return redirect(next_url)
            else:
                return render(request, 'signin.html', {'error': 'Invalid username or password'})
        # Pass 'next' to the template if present
        next_url = request.GET.get('next', '')
        return render(request, 'signin.html', {'next': next_url})
    except Exception as e:
        return render(request, 'signin.html', {'error': str(e)})
@login_required(login_url='signin/')
def signout(request):
    logout(request)
    return redirect('signin/')

@login_required(login_url='signin/')
def getInstructorData(request):
    try:
        userid = request.GET.get('instructorId',None)
        if userid:
            instructor = Instructor.objects.filter(user=userid).first()
            if instructor:
                DlInfo = DLInfo.objects.filter(dlUser=instructor.user).first()
                print("DLINFO",DLInfo)
                data = {
                    'id': instructor.user.user.id,
                    'name': instructor.user.user.first_name,
                    'email': instructor.user.user.email,
                    'dob': instructor.dob,
                    'phone': instructor.user.phoneNo,
                    'branch': instructor.instructorBranch.branchName,
                    # 'vehicle': instructor.instructorVehicle.id,
                    'bloodGroup': instructor.user.bloodGroup,
                    'profilePic': instructor.user.profilePic.url if instructor.user.profilePic else '',
                    'dlNo': DlInfo.dlNo if DlInfo else None,
                    'dlIssueDate': DlInfo.dlIssueDate if DlInfo else None,
                    'dlExpiry': DlInfo.dlExpiry if DlInfo else None,
                    'adharCard': instructor.adharCard.url if instructor.adharCard else None,
                    'aggrementDoc': instructor.aggreementDoc.url if instructor.aggreementDoc else None,
                    'policeVerificationDoc': instructor.policeVerificationDoc.url if instructor.policeVerificationDoc else None,
                }
                return success_response(data=data, message="Instructor data fetched successfully for a specific ID")
            else:
                return error_response(message="Instructor not found", status=404)
            
        else:
            instructors = Instructor.objects.all()
            data = []
            for instructor in instructors:
                if instructor.is_active == True:
                    data.append({
                        'id': instructor.user.id,
                        'name': instructor.user.user.first_name,
                        'email': instructor.user.user.email,
                        'phone': instructor.user.phoneNo,
                        'branch': instructor.instructorBranch.branchName,
                        # 'vehicle': instructor.instructorVehicle.vehicleName,
                        'bloodGroup': instructor.user.bloodGroup,
                        'profilePic': instructor.user.profilePic.url if instructor.user.profilePic else '',

                    })
            return success_response(data=data, message="Instructor data fetched successfully for all instructors")
    except Exception as e:
        return error_response(message=str(e))        
        
@csrf_exempt
@login_required(login_url='signin/')
def manage_instructor(request):
    if request.method == 'POST':
        instructorid = request.POST.get('instructorId')
        name = request.POST.get('name')
        email = request.POST.get('email',None)
        phone = request.POST.get('mobile')
        dob = request.POST.get('dob')
        branch = request.POST.get('branch')
        profilepic = request.FILES.get('profilePhoto')
        bloodGroup = request.POST.get('bloodGroup')
        dlNo = request.POST.get('dlNo')
        dlIssueDate = request.POST.get('dlIssueDate')
        dlExpiry = request.POST.get('dlExpiry')
        adharcard = request.FILES.get('adharcard')
        aggrement = request.FILES.get('aggrement')
        policeVerification = request.FILES.get('policeVerification')

        if instructorid:
            # --- UPDATE Flow ---
            try:
                instructor = Instructor.objects.get(user__id=instructorid)
                user = instructor.user.user
                user.first_name = name
                user.email = email
                user.save()

                userProfile = instructor.user
                userProfile.phoneNo = phone
                userProfile.bloodGroup = bloodGroup
                if profilepic:
                    userProfile.profilePic = profilepic
                userProfile.save()

                instructor.instructorBranch = Branch.objects.get(branchName=branch)
                instructor.dob = dob
                if adharcard:
                    instructor.adharCard = adharcard
                if aggrement:
                    instructor.aggreementDoc = aggrement
                if policeVerification:
                    instructor.policeVerificationDoc = policeVerification
                instructor.save()

                if dlNo and dlIssueDate and dlExpiry:
                    dlinfo = DLInfo.objects.get(dlUser=userProfile)
                    dlinfo.dlNo = dlNo
                    dlinfo.dlIssueDate = dlIssueDate
                    dlinfo.dlExpiry = dlExpiry
                    dlinfo.save()

                return success_response(message="Instructor updated successfully")

            except Exception as e:
                return error_response(message=str(e))

        else:
            # --- CREATE Flow ---
            newuser = None
            userprofile = None
            instructor = None
            dlInfo = None

            try:
                newuser = User.objects.create_user(
                    username=phone,
                    email=email,
                    password=dob,
                    first_name=name
                )

                userprofile = UserProfile.objects.create(
                    user=newuser,
                    phoneNo=phone,
                    is_instructor=True,
                    profilePic=profilepic,
                    bloodGroup=bloodGroup
                )

                branch_obj = Branch.objects.get(branchName=branch)

                instructor = Instructor.objects.create(
                    user=userprofile,
                    instructorBranch=branch_obj,
                    dob=dob
                )

                if adharcard:
                    instructor.adharCard = adharcard
                if aggrement:
                    instructor.aggreementDoc = aggrement
                if policeVerification:
                    instructor.policeVerificationDoc = policeVerification
                instructor.save()

                dlInfo = DLInfo.objects.create(
                    dlNo=dlNo,
                    dlIssueDate=dlIssueDate,
                    dlExpiry=dlExpiry,
                    dlUser=userprofile
                )

                return success_response(message="Instructor created successfully")

            except Exception as e:
                # Clean up partially created data
                if dlInfo:
                    dlInfo.delete()
                if instructor:
                    instructor.delete()
                if userprofile:
                    userprofile.delete()
                if newuser:
                    newuser.delete()
                return error_response(message=str(e))

    if request.method == 'DELETE':
        try:
            id = request.GET.get('instructorId')
            instructor = Instructor.objects.get(user__id=id)
            instructor.is_active = False
            instructor.save()
            return success_response(message="Instructor deleted successfully")
        except Exception as e:
            return error_response(message=str(e))

    return render(request, 'manage-instructor.html')


@login_required(login_url='signin/')
def getStudentData(request):
    studentid = request.GET.get('studentId',None)
    try:
        if studentid:
            student = Student.objects.filter(id=studentid).first()
            if not student:
                return error_response(message="Student not found", status=404)
            dlinfo = DLInfo.objects.filter(dlUser=student.user).first()
            data = {
                    'receiptNo': str(student.id) + '-' +str(datetime.today().month) + str(datetime.today().year),
                    'id': student.id,
                    'name': student.user.user.first_name,
                    'email': student.user.user.email,
                    'phone': student.user.phoneNo,
                    'dob': student.dob,
                    'applicationNo': student.applicationNo,
                    'address': student.address,
                    'branch': student.Branch.branchName,
                    'bloodGroup': student.user.bloodGroup,
                    'profilePic': student.user.profilePic.url if student.user.profilePic else '',
                    'gender': student.gender,
                    "bookingType": student.booking_Type,
                    'cource': student.cource.courceName,
                    'courceId': student.cource.id,
                    'instructor': student.instructor.user.user.first_name,
                    'instructorId': student.instructor.user.id,
                    'slotTime': f'{student.slot.slotStart} - {student.slot.slotEnd}',
                    'slotId': student.slot.id,
                    'startDate': student.courceEnrollDate,
                    'endDate': student.courceEndDate,
                    'courseFee': student.cource.courceFee,
                    'totalAmount': student.cource.courceFee + sum([addOnService.serviceFee for addOnService in student.addOnService.all()]),
                    'paymentReceived': student.amountPaid,
                    'paymentDue': student.amountPending,
                    'paymentDueDate': student.paymentDueDate,
                    'status': student.student_staus,
                    'addOnService': [(addOnService.id, addOnService.serviceName, addOnService.serviceFee) for addOnService in student.addOnService.all()],
                    'dlNo': dlinfo.dlNo if dlinfo else '',
                    'dlIssueDate': dlinfo.dlIssueDate if dlinfo else '',
                    'dlExpiry': dlinfo.dlExpiry if dlinfo else '',
                    'dlType': dlinfo.dlType if dlinfo else '',
                }
            paymetRecieved = Payment.objects.filter(student=student).order_by('-paymentDate').first()
            if paymetRecieved:
                data['paymentRecievedBy'] = paymetRecieved.paymentRecevedBy.id
                data['paymentRecievedByName'] = paymetRecieved.paymentRecevedBy.user.first_name
            return success_response(data=data, message="Student data fetched successfully for a specific ID")
        else:
            students = Student.objects.all()
            data = []
            for student in students:
                if student.is_active == True:
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

            return success_response(data=data, message="Student data fetched successfully for all students")
    except Exception as e:
        return error_response(message=str(e))
        


@csrf_exempt
@login_required(login_url='signin/')
def manage_student(request):
    if request.method == 'POST':
        id = request.POST.get('studentId')
        name = request.POST.get('studentName')
        email = request.POST.get('studentEmail',None)
        dob = request.POST.get('dob')
        applicationNo = request.POST.get('applicationNo')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        branch = request.POST.get('branch')
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
        paymentRecieved = request.POST.get('paymentReceived',None)
        paymentDue = request.POST.get('paymentDue',None)
        paymentDueDate = request.POST.get('paymentDueDate',None)
        addOnService = request.POST.get('addOnService',None)
        paymentRecievedBy = request.POST.get('paymentRecievedBy',None)
        if addOnService:
            addOnService = map(int, addOnService.split(','))
            addOnService = list(addOnService)
     
        try:
            # parse dob into a date object early
            dob_date = None
            if dob:
                try:
                    dob_date = _parse_date_string(dob)
                except ValueError as e:
                    return error_response(message=str(e), status=400)

            if Student.objects.filter(id=id).exists():
                student = Student.objects.get(id=id)
                student.user.user.first_name = name
                if email and email != '':
                    student.user.user.email = email
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
                student.cource = Cource.objects.get(id=cource)
                student.instructor = Instructor.objects.get(user_id=instructor)
                student.Branch = Branch.objects.get(branchName=branch)
                student.slot = Slot.objects.get(id=slot)
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
                if paymentRecieved:
                    student.amountPaid = paymentRecieved
                if paymentDue:
                    student.amountPending = paymentDue
                if paymentDueDate:
                    student.paymentDueDate = paymentDueDate
                # student.addOnService.clear()
                if addOnService:
                    student.addOnService.clear()
                    for addOnServiceId in addOnService:
                        student.addOnService.add(AddOnService.objects.get(id=addOnServiceId))
                student.save()
                if slot:
                    stundetHistory = StudentCouseHistory(student=student,cource=Cource.objects.get(id=cource),instructor=Instructor.objects.get(user_id=instructor),courceEnrollDate=startDate,courceCompletionDate=endDate,created_by = request.user.userprofile)
                    stundetHistory.save()

                
                return success_response(message="Student updated successfully")
            else:
                newuser = None
                userprofile = None
                Dlinfo = None
                try:
                    if User.objects.filter(username=phone).exists():
                        newuser = User.objects.get(username=phone)    
                    else:
                        # use formatted DOB (ddmmyyyy) as password
                        if not dob_date:
                            return error_response(message="DOB is required for new student", status=400)
                        dobstr = dob_date.strftime('%d%m%Y')
                        newuser = User.objects.create_user(username=phone, password=dobstr, first_name=name, email=email)

                    
                    
                    userprofile = UserProfile(user=newuser, phoneNo=phone, is_student=True, profilePic=profilepic ,bloodGroup=bloodGroup)
                    userprofile.save()
                    branch = Branch.objects.get(branchName=branch)
                    cource = Cource.objects.get(id=cource)
                    instructor = Instructor.objects.get(user__id=instructor)
                    slot = Slot.objects.get(id=slot)
                    if bookingType == 'Pre-Booking':
                        slot.slotPreBooked = True

                        slot.save()
                    else:
                        slot.slotPreBooked = False
                        slot.slotUsed = True
                        slot.save()
                    if paymentDueDate == "":
                        paymentDueDate = None
                    

                    student = Student(user=userprofile, applicationNo=applicationNo, dob=dob_date, address=address,Branch=branch,gender=gender, cource=cource, instructor=instructor, slot=slot,courceEnrollDate=startDate,courceEndDate = endDate,amountPaid=paymentRecieved,amountPending=paymentDue,paymentDueDate=paymentDueDate,booking_Type=bookingType)
                    # paymentBy = Instructor.objects.get(user__id=paymentRecievedBy) 
                    print("stdent",student)
                    payment = Payment(student=student,paymentDate=datetime.today().date(),paymentAmount=paymentRecieved,paymentMethod='Cash',paymentRecevedBy=UserProfile.objects.get(id=paymentRecievedBy))
                    print("payment",payment)
                    print(addOnService)
                    student.save()
                    addontoatal = 0
                    if addOnService:
                        for addOn in addOnService:
                            addOnService = AddOnService.objects.get(id=addOn)
                            student.addOnService.add(addOnService)
                            addontoatal= addontoatal + int(addOnService.serviceFee)
                        
                    # student.amountPending = int(student.amountPending) + addontoatal
                    student.save()

                    
                    payment.save()
                    if dlNo:
                        print("DLINFO",dlNo)
                        dlinfo = DLInfo.objects.create(dlNo=dlNo, dlIssueDate=dlIssueDate, dlExpiry=dlExpiry, dlUser=userprofile,dlType=dlType)
                        dlinfo.save()
                    
                    stundetHistory = StudentCouseHistory(student=student,cource=cource,instructor=instructor,courceEnrollDate=startDate,courceCompletionDate=endDate,created_by=userprofile)
                    stundetHistory.save()
                    
                    return success_response(data={'receiptNo':str(student.id) + '-' +str(datetime.today().month) + str(datetime.today().year)},message="Student created successfully")
                except Exception as e:
                    print(e)
                    if newuser:
                        newuser.delete()
                        if bookingType == 'Pre-Booking':
                            slot.slotPreBooked = False
                        else:
                            slot.slotUsed = False
                        slot.save() 
                    return error_response(message=str(e))

        except Exception as e:
                return error_response(message=str(e))
    if request.method == 'DELETE':
        try:
            id = request.GET.get('studentId')
            student = Student.objects.get(id=id)
            student.slot.slotPreBooked = False
            student.slot.slotUsed = False
            student.slot.save()
            userProf = UserProfile.objects.get(id=student.user.id)
            print(userProf)
            user = User.objects.get(id=userProf.user.id)
            userProf.delete()
            student.delete()
            user.delete()
            return success_response(message="Student deleted successfully")
        except Exception as e:
            print(e)
            return error_response(message=str(e))


    return render(request, 'manage-student.html')

@login_required(login_url='signin/')
def getBranchAdminData(request):
    try:
        users = UserProfile.objects.filter(is_branchAdmin=True)
        if not users:
            return error_response(message="No branch admin found", status=404)
        
        data = []
        for user in users:
            data.append({
                'id': user.id,
                'name': user.user.first_name,
            })
        return success_response(data=data, message="Branch admin data fetched successfully")
    except Exception as e:
        return error_response(message=str(e))

@login_required(login_url='signin/')
def getBranchData(request):
    branchid = request.GET.get('branchId',None)
    try:
        if branchid:
            branch = Branch.objects.filter(id=branchid).first()
            if not branch:
                return error_response(message="Branch not found", status=404)
            data = {
                    'id': branch.id,
                    'branchName': branch.branchName,
                    'branchAddress': branch.branchAddress,
                    'branchPhoneNo': branch.branchPhoneNo,
                    'branchEmail': branch.branchEmail,
                    'branchIncharge': branch.branchIncharge.user.first_name,
                    'branchInchargeId': branch.branchIncharge.id,
                }
            return success_response(data=data, message="Branch data fetched successfully for a specific ID")
        else:
                branches = Branch.objects.all()
                data = []
                for branch in branches:
                    data.append({
                        'id': branch.id,
                        'branchName': branch.branchName,
                        'branchAddress': branch.branchAddress,
                        'branchPhoneNo': branch.branchPhoneNo,
                        'branchEmail': branch.branchEmail,
                        'branchIncharge': branch.branchIncharge.user.first_name,
                    })
                return success_response(data=data, message="Branch data fetched successfully for all branches")
    except Exception as e:
        return error_response(message=str(e))
@csrf_exempt
@login_required(login_url='signin/')
def manage_branch(request):
    if request.method == 'POST':
        id = request.POST.get('branchId')
        branchName = request.POST.get('branchName')
        branchAddress = request.POST.get('branchAddress')
        branchPhoneNo = request.POST.get('branchPhoneNo')
        branchEmail = request.POST.get('branchEmail')
        branchIncharge = request.POST.get('branchIncharge')
        try:
            if Branch.objects.filter(id=id).exists():
                branch = Branch.objects.get(id=id)
                branch.branchName = branchName
                branch.branchAddress = branchAddress
                branch.branchEmail = branchEmail
                branch.branchPhoneNo = branchPhoneNo
                branch.branchIncharge = UserProfile.objects.get(id=branchIncharge)
                branch.save()
                return success_response(message="Branch updated successfully")
            else:
    
                    user = UserProfile.objects.get(id=branchIncharge)
                    branch = Branch(branchName=branchName, branchAddress=branchAddress, branchPhoneNo=branchPhoneNo, branchEmail=branchEmail, branchIncharge=user)
                    user = UserProfile.objects.get(id=branchIncharge)
                    user.is_branchAdmin = True
                    user.save()
                    branch.save()
                    return success_response(message="Branch created successfully")
        except Exception as e:
            return error_response(message=str(e))
    if request.method == 'DELETE':
        try:
            id = request.GET.get('branchId')
            branch = Branch.objects.get(id=id)
            branch.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    
    return render(request, 'manage-branch.html')

@login_required(login_url='signin/')
def getVehicleData(request):
    vehicalId = request.GET.get('vehicleId', None)
    
    try:
        if vehicalId:
            vehicle = Vehicle.objects.filter(id=vehicalId).first()
            if not vehicle:
                return error_response(message="Vehicle not found", status=404)
            vehicalData = {
                'id': vehicle.id,
                'vehicalName': vehicle.vehicleName,
                'vehicleNo': vehicle.vehicleNo,
                'vehicleType': vehicle.vehicleType,
                'insuranceValidity': vehicle.insuranceValidity.strftime('%Y-%m-%d'),
                'pollutionValidity': vehicle.pollutionValidity.strftime('%Y-%m-%d'),
                'fitnessValidity': vehicle.fitnessValidity.strftime('%Y-%m-%d'),
                'qrCodeImage': vehicle.qrCodeImage.url if vehicle.qrCodeImage else None
            }
            return success_response(data=vehicalData, message="Vehicle data fetched successfully for a specific ID")
        else:
            vehicle = Vehicle.objects.all()
            vehicalData = []
            for i in vehicle:
                vehicalData.append({
                    'id': i.id,
                    'vehicalName': i.vehicleName,
                    'vehicleNo': i.vehicleNo,
                    'vehicleType': i.vehicleType,
                    'insuranceValidity': i.insuranceValidity.strftime('%Y-%m-%d'),
                    'pollutionValidity': i.pollutionValidity.strftime('%Y-%m-%d'),
                    'fitnessValidity': i.fitnessValidity.strftime('%Y-%m-%d'),
                    'branch': i.vehicleBranch.branchName,
                    'qrCodeImage': i.qrCodeImage.url if i.qrCodeImage else None
                })
            
            return success_response(data=vehicalData, message="Vehicle data fetched successfully for all vehicles")
    except Exception as e:
        return error_response(message=str(e))
@csrf_exempt
@login_required(login_url='signin/')
def manage_vehicle(request):
    if request.method == 'POST':
        vehicleNo = request.POST.get('vehicleNo')
        vehicleName = request.POST.get('vehicleName')
        vehicleType = request.POST.get('vehicleType')
        vehicleBranch = request.POST.get('vehicleBranch')
        insuranceValidity = request.POST.get('insuranceValidity')
        pollutionValidity = request.POST.get('pollutionValidity')
        fitnessValidity = request.POST.get('fitnessValidity')
        slotTimeStrat = request.POST.get('slotTimeStart')
        slotTimeEnd = request.POST.get('slotTimeEnd')
        lunchTimeStart = request.POST.get('lunchTimeStart')
        lunchTimeEnd = request.POST.get('lunchTimeEnd')
        slotDuration = int(request.POST.get('slotDuration'))

        
        

        # Check if vehicle exists and update, otherwise create a new one


        if Vehicle.objects.filter(vehicleNo=vehicleNo).exists():
            vehicle = Vehicle.objects.get(vehicleNo=vehicleNo)
            vehicle.vehicleName = vehicleName
            vehicleNo = vehicleNo
            vehicle.vehicleType = vehicleType
            vehicle.insuranceValidity = insuranceValidity
            vehicle.pollutionValidity = pollutionValidity
            vehicle.fitnessValidity = fitnessValidity
            vehicle.save()
            return JsonResponse({'success': 'Vehicle updated successfully'})

        else:
            try:
                
                vehicle = Vehicle.objects.create(vehicleNo=vehicleNo,vehicleName=vehicleName,vehicleType=vehicleType,vehicleBranch=Branch.objects.get(id=vehicleBranch),insuranceValidity=insuranceValidity,pollutionValidity=pollutionValidity,fitnessValidity=fitnessValidity,is_active=True)
                vehicle.save()
                
                start_time = datetime.strptime(slotTimeStrat, '%H:%M').time()
                end_time = datetime.strptime(slotTimeEnd, '%H:%M').time()
                lunch_start = datetime.strptime(lunchTimeStart, '%H:%M').time()
                lunch_end = datetime.strptime(lunchTimeEnd, '%H:%M').time()
                today = datetime.now().date()
                current_time = datetime.combine(today, start_time)
                end_datetime = datetime.combine(today, end_time)
                lunch_start_datetime = datetime.combine(today, lunch_start)
                lunch_end_datetime = datetime.combine(today, lunch_end)
                
                
                
                while current_time < end_datetime:
                    # Calculate slot end time
                    slot_end_time = current_time + timedelta(minutes=slotDuration)
                    
                    # Check if slot would go beyond the end time
                    if slot_end_time > end_datetime:
                        break
                        
                    # Check if slot overlaps with lunch time
                    slot_overlaps_lunch = (
                        (current_time < lunch_end_datetime and slot_end_time > lunch_start_datetime)
                    )
                    
                    if not slot_overlaps_lunch:
                        # Create the slot
                        slot = Slot.objects.get_or_create(
                            vehicle=vehicle,
                            slotStart=current_time.time(),
                            slotEnd=slot_end_time.time(),
                            slotBranch=vehicle.vehicleBranch,
                            defaults={
                                'slotUsed': False,
                                'slotPreBooked': False
                            }
                        )
                    print(f"Slot created: {current_time.time()} to {slot_end_time.time()} for vehicle {vehicle.vehicleName}")
                    # Move to next slot
                    current_time = slot_end_time
                    
                    # If we just finished a slot before lunch, skip to after lunch
                    if current_time <= lunch_start_datetime and current_time + timedelta(minutes=slotDuration) > lunch_start_datetime:
                        current_time = lunch_end_datetime
                return JsonResponse({'success': 'Vehicle Added successfully'})
                
            except Exception as e:
                print(e)
                if vehicle:
                    vehicle.delete()
                return JsonResponse({'error': 'Error creating vehicle'}, status=400)

    if request.method == 'DELETE':
        try:
            id = request.GET.get('vehicleId')
            vehicle = Vehicle.objects.get(id=id)
            vehicle.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return render(request, 'manage-vehicle.html')
 


@login_required(login_url='signin/')
def getCourseData(request):
    courseId = request.GET.get('courseId', None)
    try:
        if courseId:
            course = Cource.objects.filter(id=courseId).first()
            if not course:
                return error_response(message="Course not found", status=404)
            courseData = {
                'id': course.id,
                'courseName': course.courceName,
                'courseDuration': course.courceDuration,
                'courceDescription': course.courceDescription,
                'courseFee': course.courceFee,
                'courceVehicle': course.vehicle.id,
                'courseBranch': course.Branch.branchName,
                'courseBranchId': course.Branch.id,
                'total_session': course.total_session
            }
            return success_response(data=courseData, message="Course data fetched successfully for a specific ID")
        else:
            course = Cource.objects.all()
            courseData = []
            for i in course:
                if i.is_active == True:
                    courseData.append({
                        'id': i.id,
                        'courseName': i.courceName,
                        'courseDuration': i.courceDuration,
                        'courseFee': i.courceFee,
                        'courceVehicle': i.vehicle.vehicleName,
                        'courseBranch': i.Branch.branchName
                    })
            
            return success_response(data=courseData, message="Course data fetched successfully for all courses")
    except Exception as e:
        return error_response(message=str(e))
@csrf_exempt
@login_required(login_url='signin/')
def manage_course(request):
    if request.method == 'POST':
        courceId = request.POST.get('courseId',None)
        courseName = request.POST.get('courseName')
        courseDuration = request.POST.get('courseDuration')
        courceDescription = request.POST.get('courceDescription')
        courseFee = request.POST.get('courseFee')
        courseVehicle = request.POST.get('courseVehicle')
        courseBranch = request.POST.get('courseBranch')
        totalsession = request.POST.get('courseSession')
        
        if Cource.objects.filter(id=courceId).exists():
            try:
                course = Cource.objects.filter(id=courceId).first()
                if not course:
                    return error_response(message="Course not found", status=404)
                if course.is_active == False:
                    return error_response(message="Cannot update an inactive course", status=400)
                course.courceName = courseName
                course.courceDuration = courseDuration
                course.courceDescription = courceDescription
                course.courceFee = courseFee
                course.total_session = totalsession
                course.vehicle = Vehicle.objects.get(id=courseVehicle)
                course.Branch = Branch.objects.get(id=courseBranch)
                course.save()
                return success_response(message="Course updated successfully")
            except Exception as e:
                
                return error_response(message=str(e))
        else:
            try:
                course = Cource.objects.create(
                    courceName=courseName,
                    courceDuration=courseDuration,
                    courceDescription=courceDescription,
                    courceFee=courseFee,
                    vehicle=Vehicle.objects.get(id=courseVehicle),
                    Branch=Branch.objects.filter(id=courseBranch).first(),
                    total_session = totalsession
                )
                course.save()
                return success_response(message="Course created successfully")
            except Exception as e:
                return error_response(message=str(e))

    if request.method == 'DELETE':
            courseId = request.GET.get('courseId',None)
            try:

                course = Cource.objects.filter(id=courseId).first()
                if not course:
                    return error_response(message="Course not found", status=404)
                
                course.is_active = False

                return success_response(message="Course deleted successfully")
            except Exception as e:
                return error_response(message=str(e))

    return render(request, 'manage-course.html')

@login_required(login_url='signin/')
def getComplainData(request):
    complainId = request.GET.get('complainId', None)
    try:
        if complainId:
            complain = Complain.objects.filter(id=complainId).first()
            if not complain:
                return error_response(message="Complain not found", status=404)
            complainData = {
                'id': complain.id,
                'complainName': complain.compalainTitle,
                'complainDescription': complain.complainDescription,
                'complainDate': complain.created_at,
                'complainStatus': complain.complainResolved,
                'complainBranch': complain.complainBranch.branchName,
                'complainFrom': complain.compalainForm.user.user.first_name,
                'complainFor': complain.compalainFor.user.first_name
            }
            return success_response(data=complainData, message="Complain data fetched successfully for a specific ID")
        else:
            complain = Complain.objects.all()
            complainData = []
            for i in complain:
                complainData.append({
                'id': i.id,
                'complainName': i.compalainTitle,
                'complainDescription': i.complainDescription,
                'complainDate': i.created_at.date(),
                'complainStatus': i.complainResolved,
                'complainBranch': i.complainBranch.branchName,
                'complainFrom': i.compalainForm.user.user.first_name,
                'complainFor': i.compalainFor.user.first_name
                })
            
            return success_response(data=complainData, message="Complain data fetched successfully for all complains")
    except Exception as e:
        return error_response(message=str(e))
@csrf_exempt
@login_required(login_url='signin/')
def manage_complain(request):
    if request.method == 'POST':
        complainId = request.POST.get('complainId')
        action_taken = request.POST.get('actionTaken')

        try:
            complain = Complain.objects.filter(id=complainId).first()
            if not complain:
                return error_response(message="Complain not found", status=404)
            complain.action_taken = action_taken
            complain.resolved_by = request.user
            complain.resolved_at = datetime.now()
            complain.complainResolved = True
            complain.save()
            return success_response(message="Complain updated successfully")
        except Exception as e:
            return error_response(message=str(e))
    return render(request, 'manage-complain.html')

# def DeleteALlComplain(request):
#     complain = Complain.objects.all()
#     complain.delete()
#     return JsonResponse({'status': 'success'})
@login_required(login_url='signin/')
def getcourceContentData(request):
    courceContentId = request.GET.get('courceContentId', None)
    try:
        if courceContentId:
            courceContent = CourceContent.objects.filter(id=courceContentId).first()
            if not courceContent:
                return error_response(message="CourceContent not found", status=404)
            
            courceContentData = {
                'id': courceContent.id,
                'courceContentDescription': courceContent.contentDescription,
                'courcecontentFile': courceContent.contentFile.url if courceContent.contentFile else '',
                'courceContentVideo': courceContent.contentVideo.url if courceContent.contentVideo else '',
            }
            return success_response(data=courceContentData, message="CourceContent data fetched successfully for a specific ID")
        else:
            courceContent = CourceContent.objects.all()
            courceContentData = []
            for i in courceContent:
                courceContentData.append({
                'id': i.id,
                'courceContentDescription': i.contentDescription,
                'courcecontentFile': i.contentFile.url if i.contentFile else '',
                'courceContentVideo': i.contentVideo.url if i.contentVideo else '',
                })
            
            return success_response(data=courceContentData, message="CourceContent data fetched successfully for all CourceContents")
    except Exception as e:
        return error_response(message=str(e))
    
@csrf_exempt
@login_required(login_url='signin/')
def manageCourseContent(request):
    if request.method == 'POST':
        courceContentId = request.POST.get('courceContentId',None)
        courcedesc = request.POST.get('courseContentDescription')
        courcefile = request.FILES.get('courseContentFile',None)
        courcevideo = request.FILES.get('courseContentVideo',None)
        try:
            if courceContentId:
                    courceContent = CourceContent.objects.filter(id=courceContentId).first()
                    if not courceContent:
                        return error_response(message="CourceContent not found", status=404)
                    courceContent.contentDescription = courcedesc
                    if courcefile:
                        courceContent.contentFile = courcefile
                    if courcevideo:
                        courceContent.contentVideo = courcevideo
                    courceContent.save()
                    return success_response(message="CourceContent updated successfully")
               
            else:
               
                    courceContent = CourceContent(contentDescription=courcedesc,contentFile=courcefile,contentVideo=courcevideo)
                    courceContent.save()
                    return success_response(message="CourceContent created successfully")
                
        except Exception as e:
            return error_response(message=str(e))
    if request.method == 'DELETE':
        courceContentId = request.GET.get('courceContentId', None)
        try:
            courceContent = CourceContent.objects.filter(id=courceContentId).first()
            if not courceContent:
                return error_response(message="CourceContent not found", status=404)
            courceContent.delete()
            return success_response(message="CourceContent deleted successfully")
        except Exception as e:
            return error_response(message=str(e))
    return render(request, 'manage-coursecontent.html')

@login_required(login_url='signin/')
def getSlotsData(request):
    # slotsId = request.GET.get('slotId', None)
    courseId = request.GET.get('courseId', None)
    bookingType = request.GET.get('bookingType', None)
    try:
        course = Cource.objects.filter(id=courseId).first()
        if not course:
            return JsonResponse({'error': 'Course not found'}, status=404)
       
        slots = Slot.objects.filter(vehicle=course.vehicle).all()
        slotData = []
        if not bookingType:
            for i in slots:
                if not i.slotUsed:
                    slotData.append({
                        'id': i.id,
                        'slotStartTime': i.slotStart,
                        'slotEndTime': i.slotEnd,
                        'slotBranch': i.slotBranch.branchName,
                        'slotUsed': i.slotUsed,
                        'slotPreBooked': i.slotPreBooked,
                        # 'UsedTill': Student.objects.filter(slot=i).last().courceEndDate if Student.objects.filter(slot=i).exists() else None
                    })
        if bookingType == 'Pre-Booking':
            slots =  Slot.objects.filter(vehicle=course.vehicle).all()
            for i in slots:
                    slotData.append({
                        'id': i.id,
                        'slotStartTime': i.slotStart,
                        'slotEndTime': i.slotEnd,
                        'slotBranch': i.slotBranch.branchName,
                        'slotUsed': i.slotUsed,
                        'slotPreBooked': i.slotPreBooked,
                        'UsedTill': Student.objects.filter(slot=i).last().courceEndDate if Student.objects.filter(slot=i).exists() else None
                    })

        return success_response(data=slotData, message="Slot data fetched successfully")
        
        
    except Exception as e:
        return error_response(message=str(e))

@csrf_exempt
@login_required(login_url='signin/')
def manageSlots(request):
    if request.method == 'POST':
        slotsId = request.POST.get('slotId',None)
        slotname = request.POST.get('slotName')
        slotstart = request.POST.get('slotStartTime')
        slotend = request.POST.get('slotEndTime')
        slotbranch = request.POST.get('slotBranch')
        try:
            if slotsId:
                try:
                    slots = Slot.objects.get(id=slotsId)
                    slots.slotName = slotname
                    slots.slotStart = slotstart
                    slots.slotEnd = slotend
                    slots.slotBranch = Branch.objects.get(branchName=slotbranch)
                    slots.save()
                    return JsonResponse({'success': 'Slot updated successfully'})
                except Exception as e:
                    return JsonResponse({'error': 'Slot not updated'}, status=404)
            else:
                try:
                    slots = Slot(slotName=slotname,slotStart=slotstart,slotEnd=slotend,slotBranch=Branch.objects.get(branchName=slotbranch))
                    slots.save()
                    return JsonResponse({'success': 'Slot added successfully'})
                except Exception as e:
                    return JsonResponse({'error': 'Slot not added'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
    if request.method == 'DELETE':
        slotsId = request.GET.get('slotId', None)
        try:
            if slotsId:
                slots = Slot.objects.get(id=slotsId)
                slots.delete()
                return JsonResponse({'success': 'Slot deleted successfully'})
            else:
                return JsonResponse({'error': 'No slot ID provided'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return render(request, 'manage-slots.html')


@login_required(login_url='signin/')
def getAttendanceData(request):
    attendanceId = request.GET.get('attendanceId', None)
    VehicleName = request.GET.get('vehicleName', None)
    branch = request.GET.get('branchName', None)
    id = request.GET.get('studentId', None)
    # startDate = request.GET.get('startDate', None)
    # endDate = request.GET.get('endDate', None)
    try:
        if id:
                attendance = Attendance.objects.filter(student__id=id)
                attendanceData = []
                for i in attendance:
                    time1 = i.timeIn
                    time2 = i.timeOut
                    date = i.date
                    if time1 and time2:
                        date1 = datetime.combine(date, time1)
                        date2 = datetime.combine(date, time2)
                        diff = date2 - date1
                    else:
                        diff = None                
                    data = {
                        'id': i.id,
                        'student': i.student.user.user.first_name,
                        'studentId': i.student.id,
                        'date': i.date,
                        'timeIn': i.timeIn,
                        'timeOut': i.timeOut,
                        'totalTime': int(diff.total_seconds() / 60) if diff else None,
                        'status': i.status,
                        'duration': diff,
                    }
                    
                    attendanceData.append(data)
                data = lambda x: x['date']
                attendanceData.sort(key=data)
                return success_response(data=attendanceData, message="Attendance data fetched successfully for a specific student")
            
        
        else:
                student = Student.objects.all()
                student = student.filter(id__in=Attendance.objects.all().values_list('student', flat=True))
                if VehicleName:
                    student = student.filter(instructor__instructorVehicle__vehicleName=VehicleName)
                if branch:
                    student = student.filter(Branch__branchName=branch)
                # student  = student.filter(student = Attendance.objects.all())
                print("Student",student)
                studentData = []
                for i in student:
                    if i.is_active == True:
                        data = {
                            'id': i.id,
                            'student': i.user.user.first_name,
                            'studentId': i.id,
                            'courceName': i.cource.courceName,
                            'startDate': i.courceEnrollDate,
                            'endDate': i.courceEndDate,
                            'attened_session': i.attened_session,
                            'total_session' : i.cource.total_session,
                            'duration': i.cource.courceDuration,
                        }
                        studentData.append(data)
                return success_response(data=studentData, message="Student data fetched successfully for all students with attendance records")
            
    except Exception as e:
        return error_response(message=str(e))
@csrf_exempt
@login_required(login_url='signin/')
def manageAttendance(request):
    if request.method == 'POST':
        attendanceId = request.POST.get('attendanceId',None)
        reason = request.POST.get('reason',None)
        student = request.POST.get('studentName')
        date = request.POST.get('attendanceDate')
        inTime = request.POST.get('inTime',None)
        outTime = request.POST.get('outTime',None)
        sessionCount = request.POST.get('session',None)
        status = request.POST.get('attendanceStatus')

        try:
            if attendanceId:
                try:
                    attendance = Attendance.objects.get(id=attendanceId)

                    attendance.is_active = False
                    attendance.reason = reason
                    attendance.save()
                    # attendance.student = Student.objects.get(id=student)
                    # attendance.date = date
                    # attendance.timeIn = inTime
                    # attendance.timeOut = outTime
                    # attendance.status = status
                    # attendance.created_by = UserProfile.objects.get(user=request.user)
                    # attendance.save()
                    # student = Student.objects.get(id=student)
                    # student.attened_session = int(student.attened_session) - int(sessionCount)
                    # # print("sa",student.attened_session)
                    # student.save()
                    return JsonResponse({'success': 'Attendance updated successfully'})
                except Exception as e:
                    return JsonResponse({'error': 'Attendance not updated'}, status=404)
            else:
                try:
                    attendance = Attendance(student=Student.objects.get(id=student),date=date,timeIn=inTime,timeOut=outTime,status=status,created_by=UserProfile.objects.get(user=request.user))
                    attendance.save()
                    if status == 'Present':
                        student = Student.objects.get(id=student)
                        student.attened_session = int(student.attened_session) + int(sessionCount)
                        student.save()
                        return JsonResponse({'success': 'Attendance added successfully'})
                    if status == 'Leave':
                        try:
                            student = Student.objects.get(id=student)
                            previous_date = student.courceEndDate
                            next_day = student.courceEndDate + timedelta(days=1)
                            if next_day.weekday() == 6:
                                next_day = next_day + timedelta(days=1)
                            student.courceEndDate = next_day
                            student.save()
                            previous_date = previous_date.strftime('%d-%m-%Y')
                            courceEndDate = student.courceEndDate.strftime('%d-%m-%Y')
                            notification = Notification.objects.create(
                                notificationTitle = f"{student.user.user.first_name}'s Course End Date Changed from {previous_date} to {courceEndDate}",
                                notificationDate = datetime.today().date(),
                                notificationTime = datetime.today().time(),
                                notificationBranch = student.Branch,

                            )
                            notification.save()

                        except Exception as e:
                            print(e)
                            # delete the attendance 
                            attendance.delete()

                            return JsonResponse({'error': 'Attendance not added'}, status=404) 
                        return JsonResponse({'success': 'Attendance added successfully'})
                          
                except Exception as e:
                    if "UNIQUE constraint failed" in str(e): #check for unique constraint violation.
                        return JsonResponse({'error': 'Attendance already Added'}, status=400)
                    print(e)
                    return JsonResponse({'error': 'Attendance not added'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
    if request.method == 'DELETE':
        studentId = request.GET.get('studentId', None)
        try:
            if studentId:
                attendance = Attendance.objects.filter(student = studentId)
                attendance.delete()
                return JsonResponse({'success': 'Attendance deleted successfully'})
            else:
                return JsonResponse({'error': 'No attendance ID provided'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'manage-attendance.html')
@login_required(login_url='signin/')
def getUserProfileData(request):
    try:
        users = UserProfile.objects.all()
        userData = []
        for i in users:
            data = {
                'id': i.id,
                'Name': i.user.first_name,
            }
            userData.append(data)
        # return JsonResponse(userData,safe=False)
        return success_response(data=userData, message="User data fetched successfully for all users")
    except Exception as e:
        return error_response(message=str(e))
@login_required(login_url='signin/')
def getDlInfoData(request):
    dlinfo = request.GET.get('dlId', None)
    try:
        if dlinfo:
            dlinfo = DLInfo.objects.filter(id=dlinfo).first()
            if not dlinfo:
                return JsonResponse({'error': 'DlInfo not found'}, status=404)
            data = {
                'id': dlinfo.id,
                'Name': dlinfo.dlUser.user.first_name,
                'userID': dlinfo.dlUser.id,
                'dlNo': dlinfo.dlNo,
                'dlIssueDate': dlinfo.dlIssueDate,
                'dlExpiry': dlinfo.dlExpiry,
                'dlType': dlinfo.dlType,
            }
            return success_response(data=data, message="DlInfo data fetched successfully for a specific ID")
        
        dlInfo = DLInfo.objects.all()
        dlInfoData = []
        for i in dlInfo:
            data = {
                'id': i.id,
                'Name': i.dlUser.user.first_name,
                # 'userID': i.dlUser.id,
                'dlNo': i.dlNo,
                'dlIssueDate': i.dlIssueDate,
                'dlExpiry': i.dlExpiry,
                'dlType': i.dlType,
            }
            dlInfoData.append(data)
        return success_response(data=dlInfoData, message="DlInfo data fetched successfully for all DlInfo") 
    except Exception as e:
        return error_response(message=str(e))
@login_required(login_url='signin/')
@csrf_exempt
def manageDlInfo(request):
    if request.method == 'POST':
        dlId = request.POST.get('dlId',None)
        dlNo = request.POST.get('dlNo')
        dlIssueDate = request.POST.get('dlIssueDate')
        dlExpiry = request.POST.get('dlExpiryDate')
        dlType = request.POST.get('dlType')
        dlUser = request.POST.get('dlUser')

        try:
            if dlId:
                    dlinfo = DLInfo.objects.get(id=dlId)
                    dlinfo.dlNo = dlNo 
                    dlinfo.dlIssueDate = dlIssueDate
                    dlinfo.dlExpiry = dlExpiry
                    dlinfo.dlType = dlType
                    dlinfo.dlUser = UserProfile.objects.get(id=dlUser)
                    dlinfo.save()
                    return success_response(message="DlInfo updated successfully")
            else:
                
                    dlUser = UserProfile.objects.get(id=dlUser)
                    dlinfo = DLInfo(dlNo=dlNo,dlIssueDate=dlIssueDate,dlExpiry=dlExpiry,dlType=dlType,dlUser=dlUser)
                    dlinfo.save()
                    return success_response(message="DlInfo added successfully")
        except Exception as e:
            if "UNIQUE constraint failed" in str(e): #check for unique constraint violation.
                return error_response(message="DlInfo already Added", status=400)
            
            return error_response(message=str(e), status=400)        
    if request.method == 'DELETE':
        dlId = request.GET.get('dlId', None)
        try:
                dlinfo = DLInfo.objects.filter(id=dlId).first()
                if not dlinfo:
                    return error_response(message="DlInfo not found", status=404)
                dlinfo.delete()
                return success_response(message="DlInfo deleted successfully")
        except Exception as e:
            return error_response(message=str(e), status=400)
        
    return render(request, 'manage-DlInfo.html')

@login_required(login_url='signin/')
def getPaymentData(request):
    try:
        three_days_ago = datetime.today() - timedelta(days=3)
        payments = Payment.objects.filter(paymentDate__gte=three_days_ago)
        
        paymentData = []
        for i in payments:
            data = {
                'id': i.id,
                'Name': i.student.user.user.first_name,
                'studentID': i.student.id,
                'paymentAmount': i.paymentAmount,
                'paymentDate': i.paymentDate,
                'paymentRecevedBy': i.paymentRecevedBy.id,
                'paymentReceivedByName': i.paymentRecevedBy.user.first_name,
                'paymentMethod': i.paymentMethod,
            }
            paymentData.append(data)
        return success_response(data=paymentData, message="Payment data fetched successfully for all payments")
    except Exception as e:
        return error_response(message=str(e))
    

@csrf_exempt
@login_required(login_url='signin/')
def managePayment(request):
    if request.method == 'POST':
        paymentId = request.POST.get('paymentId',None)
        paymentAmount = request.POST.get('paymentReceived')
        paymentDate = request.POST.get('paymentDate')
        paymentBy = request.POST.get('paymentReceivedBy')
        paymentMode = request.POST.get('paymentMethod')
        studentId = request.POST.get('studentId')
        student = request.POST.get('studentName')

        try:
            if paymentId:
                payment = Payment.objects.filter(id=paymentId).first()
                if not payment:
                    return error_response(message="Payment not found", status=404)
                payment.paymentAmount = paymentAmount
                payment.paymentDate = paymentDate
                payment.paymentRecevedBy = UserProfile.objects.get(id=paymentBy)
                payment.paymentMethod = paymentMode
                payment.save()
                student =  Student.objects.get(id=studentId)
                student.amountPaid = student.amountPaid + int(paymentAmount)
                student.amountPending = student.amountPending - int(paymentAmount)
                student.save()
                return success_response(message="Payment updated successfully")
            else:
                student = Student.objects.filter(id=studentId).first()
                if not student:
                    return error_response(message="Student not found", status=404)
                
                print("Student",student)
                payment =  Payment(student = Student.objects.get(id=studentId),paymentAmount=paymentAmount,paymentDate=paymentDate,paymentRecevedBy=UserProfile.objects.get(id=paymentBy),paymentMethod=paymentMode)
                payment.save()
                student =  Student.objects.get(id=studentId)
                student.amountPaid = student.amountPaid + int(paymentAmount)
                student.amountPending = student.amountPending - int(paymentAmount)
                student.save()
                
                return success_response(message="Payment added successfully")
        except Exception as e:
            return error_response(message=str(e))
        
@login_required(login_url='signin/')
def getAddOnServiceData(request):
    addOnServiceId = request.GET.get('serviceId', None)

    try:
        if addOnServiceId:
            addOnService = AddOnService.objects.filter(id=addOnServiceId).first()
            if not addOnService:
                return error_response(message="Add On Service not found")
            data = {
                'id': addOnService.id,
                'addOnServiceName': addOnService.serviceName,
                'addOnServiceAmount': addOnService.serviceFee,
                'mandetory': addOnService.mandetory,
            }
            return success_response(data=data, message="Add On Service data fetched successfully for a specific ID")
        else:
            addOnServices = AddOnService.objects.all()
            addOnServiceData = []
            for i in addOnServices:
                data = {
                    'id': i.id,
                    'addOnServiceName': i.serviceName,
                    'addOnServiceAmount': i.serviceFee,
                    'mandetory': i.mandetory,
                }
                addOnServiceData.append(data)
            return success_response(data=addOnServiceData, message="Add On Service data fetched successfully for all Add On Services")
    except Exception as e:
        return error_response(message=str(e))
@csrf_exempt
@login_required(login_url='signin/')
def manageAddOnService(request):
    if request.method == 'POST':
        addOnServiceId = request.POST.get('serviceId',None)
        addOnServiceName = request.POST.get('serviceName')
        addOnServiceAmount = request.POST.get('serviceFee')
        mandetory = request.POST.get('isMandatory')
        if mandetory == 'Yes':
            mandetory = True
        else:
            mandetory = False
        try:
            if addOnServiceId:
                
                addOnService = AddOnService.objects.filter(id=addOnServiceId).first()
                if not addOnService:
                    return error_response(message="Add On Service not found")
                addOnService.serviceName = addOnServiceName
                addOnService.serviceFee = addOnServiceAmount
                addOnService.mandetory = mandetory
                addOnService.save()
                return success_response(message="Add On Service updated successfully")
            else:
                addOnService = AddOnService(serviceName=addOnServiceName,serviceFee=addOnServiceAmount,mandetory=mandetory)
                addOnService.save()
                return success_response(message="Add On Service added successfully")
        except Exception as e:
            return error_response(message=str(e))

    if request.method == 'DELETE':
        addOnServiceId = request.GET.get('serviceId', None)
        try:
            addOnService = AddOnService.objects.filter(id=addOnServiceId).first()
            if not addOnService:
                return error_response(message="Add On Service not found")
            addOnService.delete()
            return success_response(message="Add On Service deleted successfully")
            
        except Exception as e:
            return error_response(message=str(e))
        
@login_required(login_url='signin/')
@csrf_exempt
def mark_bulk_attandance_inactive(request):
    """
    Mark bulk attendance as 'Leave' for all active students of an instructor.
    Uses get_or_create to avoid unique constraint errors and logs per-student failures.
    Returns counts of created vs skipped records.
    """
    if request.method != 'POST':
        return error_response(message="Invalid request method", status=405)

    instructor_id = request.POST.get('instructorId') or request.POST.get('instructor_id')
    date = request.POST.get('date',None)
    if not instructor_id:
        return error_response(message="Instructor ID not provided", status=400)

    try:
        students = Student.objects.filter(instructor=Instructor.objects.get(user__id=instructor_id), is_active=True,courceEndDate__gte=datetime.today().date())
        if not students.exists():
            return error_response(message="No active students found for the instructor", status=404)

        user_profile = UserProfile.objects.get(user=request.user)
        today = datetime.today().date()
        created_count = 0
        skipped_student_ids = []
        errors = []
        if not date:
            date = datetime.today().date()
        for student in students:
            try:
                # Create or get attendance
                created = Attendance.objects.create(
                    student=student,
                    date=date,
                    timeIn=None,
                    timeOut=None,
                    status='Leave',
                    created_by=user_profile,
                    reason='Marked as Leave Instructor On Leave',

                )

                if created:
                    created_count += 1
                else:
                    skipped_student_ids.append(student.id)

                # Update course end date
                previous_date = student.courceEndDate
                next_day = (previous_date or today) + timedelta(days=1)
                if next_day.weekday() == 6:  # Skip Sunday
                    next_day += timedelta(days=1)

                student.courceEndDate = next_day
                student.save()

                # Create notification
                previous_date_str = previous_date.strftime('%d-%m-%Y') if previous_date else ''
                courceEndDate_str = student.courceEndDate.strftime('%d-%m-%Y')

                Notification.objects.create(
                    notificationTitle=(
                        f"{student.user.user.first_name}'s Course End Date Changed "
                        f"from {previous_date_str} to {courceEndDate_str}"
                    ),
                    notificationDate=today,
                    notificationTime=datetime.today().time(),
                    notificationBranch=student.Branch,
                )

            except Exception as e:
                logger.exception("Error processing student %s: %s", student.id, e)
                errors.append(f"student:{student.id}:{str(e)}")

        return success_response(
            data={'created': created_count, 'skipped': skipped_student_ids, 'errors': errors},
            message="Bulk attendance processed"
        )

    except UserProfile.DoesNotExist:
        return error_response(message="Current user profile not found", status=401)
    except Exception as e:
        logger.exception("Error processing bulk attendance for instructor %s: %s", instructor_id, e)
        return error_response(message=str(e))

@login_required(login_url='signin/')
def getNotificationData(request):
    try:
        notifications = Notification.objects.all()
        notificationData = []
        for i in notifications:
            if i.notificationIsRead == False:
        
                data = {
                    'id': i.id,
                    'notificationTitle': i.notificationTitle,
                    'notificationTime': i.notificationTime.strftime("%I:%M %p"),
                    'notificationDate': i.notificationDate.strftime("%Y-%m-%d"),
                    'notificationBranch': i.notificationBranch.branchName,
                }
                notificationData.append(data)
        return success_response(data=notificationData, message="Notification data fetched successfully for all notifications")
    except Exception as e:
        return error_response(message=str(e))

@csrf_exempt
@login_required(login_url='signin/')
def manageNotification(request):
    if request.method == 'POST':
        notificationId = request.POST.get('notificationId',None)
        try:
            if notificationId == 'all':
                notifications = Notification.objects.filter(notificationIsRead=False)
                for notification in notifications:
                    notification.notificationIsRead = True
                    notification.save()
                return success_response(message="All notifications marked as read")
            else:
                notification = Notification.objects.filter(id=notificationId).first()
                if not notification:
                    return error_response(message="Notification not found")
                notification.notificationIsRead = True
                notification.save()
                return success_response(message="Notification marked as read")
        except Exception as e:
            return error_response(message=str(e))

            

    

    if request.method == 'DELETE':
        notificationId = request.GET.get('notificationId', None)
        try:
    
            notification = Notification.objects.filter(id=notificationId).first()
            if not notification:
                return error_response(message="Notification not found")
            notification.delete()
            return success_response(message="Notification deleted successfully")
        except Exception as e:
            return error_response(message=str(e))
