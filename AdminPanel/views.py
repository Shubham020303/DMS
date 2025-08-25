from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from datetime import datetime,timedelta
from .models import (DLInfo,Instructor,Vehicle,Cource,Student,Attendance,Branch,UserProfile,Complain,CourceContent,Slot,Payment,AddOnService,Notification)
from django.core.paginator import Paginator
# Create your views here.
@login_required(login_url='signin/')
def getReamainingPaymentData(request):
    studentid= request.GET.get('studentId',None)
    if studentid:
        student = Student.objects.get(id=studentid)
        data = {
            'name': student.user.user.first_name,
            'studentId': student.id,
            'paymentDue': student.amountPending

        }
        return JsonResponse(data, safe=False)
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
        return JsonResponse(data, safe=False)
    
@login_required(login_url='signin/')
def getSlotWiseData(request):

    slots = Slot.objects.all()
    today = datetime.today().date()
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
                    slot_data = {
                        'slotTime': f'{slot.slotStart} - {slot.slotEnd}',
                        'branch': slot.slotBranch.branchName,
                        'student': student.first().user.user.first_name if student.exists() else None,
                    }
                    temp_slot_data.append(slot_data)
                tempData['slots'] = temp_slot_data
            data.append(tempData)
    return JsonResponse(data, safe=False)
            
    # for slot in slots:
    #         student = Student.objects.filter(slot=slot,student_staus=True,booking_Type = 'Normal',courceEndDate__gte=today)
    #         for i in student:

    #             slot_data = {
                
    #                 'slotTime': f'{slot.slotStart} - {slot.slotEnd}',
    #                 'studentName': student_name,
    #                 'branch': student.Branch.branchName if student_name else None,
    #                 'vehicle':student.cource.vehicle.vehicleName if student_name else None,
    #                 'vehicles': [{vehicle.vehicleName:'True' if student.cource.vehicle.id == vehicle.id else 'False'} for vehicle in Vehicle.objects.all()],
    #                 # 'vehicle': student.instructor.instructorVehicle.vehicleName if student_name else None
    #             }
    #             if slot.slotStart < datetime.strptime('12:00', '%H:%M').time():
    #                 morning_slots.append(slot_data)
    #             else:
    #                 evening_slots.append(slot_data)
                
    # key = lambda x: x['slotTime']
    # morning_slots.sort(key=key)
    # evening_slots.sort(key=key)
    # data = {
    #         'morning': morning_slots,
    #         'evening': evening_slots
    #     }   
    # return JsonResponse(data, safe=False)
@login_required(login_url='signin/')
def getStudentOnLeaveData(request):
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
    return JsonResponse(data, safe=False)

def getEearningData(request):
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
    return JsonResponse(data, safe=False)
@login_required(login_url='signin/')
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def signin(request):
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
@login_required(login_url='signin')
def signout(request):
    logout(request)
    return redirect('signin/')

@login_required(login_url='signin/')
def getInstructorData(request):
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
                'dlNo': DlInfo.dlNo,
                'dlIssueDate': DlInfo.dlIssueDate,
                'dlExpiry': DlInfo.dlExpiry,
                'adharCard': instructor.adharCard.url if instructor.adharCard else None,
                'aggrementDoc': instructor.aggreementDoc.url if instructor.aggreementDoc else None,
                'policeVerificationDoc': instructor.policeVerificationDoc.url if instructor.policeVerificationDoc else None,


            }
            return JsonResponse(data)
        
    else:
        instructors = Instructor.objects.all()
        data = []
        for instructor in instructors:
            if instructor.user.is_active == True:
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
        return JsonResponse(data, safe=False)
        
    
@csrf_exempt
@login_required(login_url='signin/')
def manage_instructor(request):
    if request.method == 'POST':
        instructorid= request.POST.get('instructorId',None)
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('mobile')
        dob = request.POST.get('dob')
        branch = request.POST.get('branch')
        vehicle = request.POST.get('vehicle')
        profilepic = request.FILES.get('profilePhoto')
        bloodGroup = request.POST.get('bloodGroup')
        dlNo = request.POST.get('dlNo')
        dlIssueDate = request.POST.get('dlIssueDate')
        dlExpiry = request.POST.get('dlExpiry')
        adharcard = request.FILES.get('adharcard')
        aggrement  = request.FILES.get('aggrement')
        policeVerification = request.FILES.get('policeVerification')
        try:
            if instructorid:
                try:
                    instructor = Instructor.objects.get(user__id=instructorid)
                    user = User.objects.get(id=instructor.user.user.id)
                    user.first_name = name
                    user.email = email
                    user.save()
                    userProfile = UserProfile.objects.get(id=instructor.user.id)
                    userProfile.phoneNo = phone
                    userProfile.bloodGroup = bloodGroup
                    if profilepic:
                        userProfile.profilePic = profilepic
                    userProfile.save()
                    instructor.instructorBranch = Branch.objects.get(branchName=branch)
                    # instructor.instructorVehicle = Vehicle.objects.get(id=vehicle)
                    instructor.dob = dob
                    if adharcard:
                        instructor.adharCard = adharcard
                    if aggrement:
                        instructor.aggreementDoc = aggrement
                    if policeVerification:
                        instructor.policeVerificationDoc = policeVerification
                    instructor.save()
                    if dlNo and dlIssueDate and dlExpiry:
                        dlinfo = DLInfo.objects.get(dlUser=instructor.user)
                        dlinfo.dlNo = dlNo
                        dlinfo.dlIssueDate = dlIssueDate
                        dlinfo.dlExpiry = dlExpiry
                        dlinfo.save()
                    # dlinfo = DLInfo.objects.get(dlUser=userprofile)
                    # dlinfo.dlNo = dlNo
                    # dlinfo.dlIssueDate = dlIssueDate
                    # dlinfo.dlExpiry = dlExpiry
                    # dlinfo.save()
                    return JsonResponse({'status': 'success'})
                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': str(e)})
            else: 
                try:  
                    newuser = User.objects.create_user(username=email, email=email, password=dob, first_name=name)
                    userprofile = UserProfile(user=newuser, phoneNo=phone, is_instructor=True, profilePic=profilepic ,bloodGroup=bloodGroup)
                    newuser.save()
                    userprofile.save()
                    branch = Branch.objects.get(branchName=branch)
    
                    instructor = Instructor(user=userprofile, instructorBranch=branch,dob=dob)
                    dlInfo = DLInfo.objects.create(dlNo=dlNo, dlIssueDate=dlIssueDate, dlExpiry=dlExpiry, dlUser=userprofile)
                    dlInfo.save()
                    if adharcard:
                        instructor.adharCard = adharcard
                    if aggrement:
                        instructor.aggreementDoc = aggrement
                    if policeVerification:
                        instructor.policeVerificationDoc = policeVerification
                    instructor.save()
                    # dlinfo = DLInfo(dlNo=dlNo, dlIssueDate=dlIssueDate, dlExpiry=dlExpiry, dlUser=userprofile)
                    # dlinfo.save()
                    return JsonResponse({'status': 'success'})
                except Exception as e:
                    if newuser:
                        userprofile = UserProfile.objects.get(user=newuser)
                        if userprofile:
                            userprofile.delete()
                        newuser.delete()
                    if dlInfo:
                        dlInfo.delete()
                    if instructor:
                        instructor.delete()
                    return JsonResponse({'status': 'error', 'message': str(e)})
        except Exception as e:
            return JsonResponse({'status': 'error', 'Main message': str(e)})
    if request.method == 'DELETE':
        try:
            id = request.GET.get('instructorId')
            userProf = UserProfile.objects.get(id=id)
            user = User.objects.get(id=userProf.user.id)
            userProf.is_active = False
            userProf.save()
            # user.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return render(request, 'manage-instructor.html')


@login_required(login_url='signin/')
def getStudentData(request):
    studentid = request.GET.get('studentId',None)
    if studentid:
        student = Student.objects.filter(id=studentid).first()
        dlinfo = DLInfo.objects.filter(dlUser=student.user).first()
        data = {
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
                'totalAmount': int(student.amountPending) + int(student.amountPaid),
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
        return JsonResponse(data)
    else:
        students = Student.objects.all()
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
@login_required(login_url='signin/')
def manage_student(request):
    if request.method == 'POST':
        id = request.POST.get('studentId')
        name = request.POST.get('studentName')
        email = request.POST.get('studentEmail')
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
        paymentRecieved = request.POST.get('paymentReceived')
        paymentDue = request.POST.get('paymentDue')
        paymentDueDate = request.POST.get('paymentDueDate',None)
        addOnService = request.POST.get('addOnService',None)
        paymentRecievedBy = request.POST.get('paymentRecievedBy')
        if addOnService:
            addOnService = map(int, addOnService.split(','))
            addOnService = list(addOnService)
     
        try:
            if Student.objects.filter(id=id).exists():
                student = Student.objects.get(id=id)
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
                    if User.objects.filter(username=phone).exists():
                        newuser = User.objects.get(username=phone)    
                    else:
                        newuser = User.objects.create_user(username=phone, password=dob, first_name=name)
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
                    # Dlinfo = DLInfo.objects.create(dlNo=dlNo, dlIssueDate=dlIssueDate, dlExpiry=dlExpiry, dlUser=userprofile)
                    if paymentDueDate == "":
                        paymentDueDate = None

                    student = Student(user=userprofile, applicationNo=applicationNo, dob=dob, address=address,Branch=branch,gender=gender, cource=cource, instructor=instructor, slot=slot,courceEnrollDate=startDate,courceEndDate = endDate,amountPaid=paymentRecieved,amountPending=paymentDue,paymentDueDate=paymentDueDate,booking_Type=bookingType)
                    # paymentBy = Instructor.objects.get(user__id=paymentRecievedBy) 
                    payment = Payment(student=student,paymentDate=datetime.today().date(),paymentAmount=paymentRecieved,paymentMethod='Cash',paymentRecevedBy=UserProfile.objects.get(id=paymentRecievedBy))
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

                except Exception as e:
                    print(e)
                    if newuser:
                        # if userprofile:
                        #     userprofile.delete()
                        # if Dlinfo:
                        #     Dlinfo.delete()
                        newuser.delete()
                        slot.slotPreBooked = False
                        slot.slotUsed = False
                        slot.save() 

                    return JsonResponse({'status': 'error', 'message': str(e)})
                return JsonResponse({'status': 'success'})
        except Exception as e:
                
                return JsonResponse({'status': 'error', 'message': str(e)})
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
            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'error', 'message': str(e)})


    return render(request, 'manage-student.html')

@login_required(login_url='signin/')
def getBranchAdminData(request):
    users = UserProfile.objects.filter(is_branchAdmin=True,is_student=False)
    data = []
    for user in users:
        data.append({
            'id': user.id,
            'name': user.user.first_name,
        })
    return JsonResponse(data, safe=False)

@login_required(login_url='signin/')
def getBranchData(request):
    branchid = request.GET.get('branchId',None)
    if branchid:
        branch = Branch.objects.filter(id=branchid).first()
        
        data = {
                'id': branch.id,
                'branchName': branch.branchName,
                'branchAddress': branch.branchAddress,
                'branchPhoneNo': branch.branchPhoneNo,
                'branchEmail': branch.branchEmail,
                'branchIncharge': branch.branchIncharge.user.first_name,
                'branchInchargeId': branch.branchIncharge.id,
            }
        return JsonResponse(data)
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
            return JsonResponse(data, safe=False)
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

        if Branch.objects.filter(id=id).exists():
            branch = Branch.objects.get(id=id)
            branch.branchName = branchName
            branch.branchAddress = branchAddress
            branch.branchEmail = branchEmail
            branch.branchPhoneNo = branchPhoneNo
            branch.branchIncharge = UserProfile.objects.get(id=branchIncharge)
            branch.save()
            return JsonResponse({'status': 'success', 'message': 'Branch updated successfully'})
        else:
            try:
                user = UserProfile.objects.get(id=branchIncharge)
                branch = Branch(branchName=branchName, branchAddress=branchAddress, branchPhoneNo=branchPhoneNo, branchEmail=branchEmail, branchIncharge=user)
                user = UserProfile.objects.get(id=branchIncharge)
                user.is_branchAdmin = True
                user.save()
                branch.save()
                return JsonResponse({'status': 'success'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
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
    print(vehicalId)
        # Fetch a single vehicle by ID if 'vehicalId' is provided
    if vehicalId:
        vehicle = Vehicle.objects.get(id=vehicalId)
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
        print(vehicalData)
        return JsonResponse(vehicalData)
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
        
        return JsonResponse(vehicalData,safe=False)
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
    if courseId:
        course = Cource.objects.get(id=courseId)
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
        return JsonResponse(courseData)
    else:
        course = Cource.objects.all()
        courseData = []
        for i in course:
            courseData.append({
                'id': i.id,
                'courseName': i.courceName,
                'courseDuration': i.courceDuration,
                'courseFee': i.courceFee,
                'courceVehicle': i.vehicle.vehicleName,
                'courseBranch': i.Branch.branchName
            })
        
        return JsonResponse(courseData,safe=False)
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
                course = Cource.objects.get(id=courceId)
                course.courceName = courseName
                course.courceDuration = courseDuration
                course.courceDescription = courceDescription
                course.courceFee = courseFee
                course.total_session = totalsession
                course.vehicle = Vehicle.objects.get(id=courseVehicle)
                course.Branch = Branch.objects.get(id=courseBranch)
                course.save()
                return JsonResponse({'success': 'Course updated successfully'})
            except Exception as e:
                print(e)
                return JsonResponse({'error': 'Error updating course'}, status=400)
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
                return JsonResponse({'success': 'Course Create  successfully'})
            except Exception as e:
                print(e)
                return JsonResponse({'error': 'Error creating course'}, status=400)

    if request.method == 'DELETE':
            courseId = request.GET.get('courseId')
            if courseId:
                try:
                    course = Cource.objects.get(id=courseId)
                    course.delete()

                    return JsonResponse({'success': 'Course deleted successfully'})
                except Cource.DoesNotExist:
                    return JsonResponse({'error': 'Course not found'}, status=404)
            else:
                return JsonResponse({'error': 'No course ID provided'}, status=400)

    return render(request, 'manage-course.html')

@login_required(login_url='signin/')
def getComplainData(request):
    complainId = request.GET.get('complainId', None)
    if complainId:
        complain = Complain.objects.get(id=complainId)
        complainData = {
            'id': complain.id,
            'complainName': complain.compalainTitle,
            'complainDescription': complain.complainDescription,
            'complainDate': complain.complainDate,
            'complainStatus': complain.complainResolved,
            'complainBranch': complain.complainBranch.branchName,
            'complainFrom': complain.compalainForm.user.user.first_name,
            'complainFor': complain.compalainFor.user.first_name
        }
        return JsonResponse(complainData)
    else:
        complain = Complain.objects.all()
        complainData = []
        for i in complain:
            complainData.append({
            'id': i.id,
            'complainName': i.compalainTitle,
            'complainDescription': i.complainDescription,
            'complainDate': i.complainDate,
            'complainStatus': i.complainResolved,
            'complainBranch': i.complainBranch.branchName,
            'complainFrom': i.compalainForm.user.user.first_name,
            'complainFor': i.compalainFor.user.first_name
            })
        
        return JsonResponse(complainData,safe=False)
@csrf_exempt
@login_required(login_url='signin/')
def manage_complain(request):
    if request.method == 'POST':
        complainId = request.POST.get('complainId',None)
        if complainId:
            complain = Complain.objects.get(id=complainId)
            complain.complainResolved = True
            complain.save()
            return JsonResponse({'success': 'Complain Resolved successfully'})
        else:
            return JsonResponse({'error': 'No complain ID provided'}, status=400)
    return render(request, 'manage-complain.html')


# def DeleteALlComplain(request):
#     complain = Complain.objects.all()
#     complain.delete()
#     return JsonResponse({'status': 'success'})
@login_required(login_url='signin/')
def getcourceContentData(request):
    courceContentId = request.GET.get('courceContentId', None)
    if courceContentId:
        courceContent = CourceContent.objects.get(id=courceContentId)
        courceContentData = {
            'id': courceContent.id,
            'courceContentDescription': courceContent.contentDescription,
            'courcecontentFile': courceContent.contentFile.url if courceContent.contentFile else '',
            'courceContentVideo': courceContent.contentVideo.url if courceContent.contentVideo else '',
    }
        return JsonResponse(courceContentData)
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
        
        return JsonResponse(courceContentData,safe=False)
    
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
                try:
                    courceContent = CourceContent.objects.get(id=courceContentId)
                    courceContent.contentDescription = courcedesc
                    if courcefile:
                        courceContent.contentFile = courcefile
                    if courcevideo:
                        courceContent.contentVideo = courcevideo
                    courceContent.save()
                    return JsonResponse({'success': 'CourceContent updated successfully'})
                except Exception as e:
                    return JsonResponse({'error': 'CourceContent not updated'}, status=404)
            else:
                try:
                    courceContent = CourceContent(contentDescription=courcedesc,contentFile=courcefile,contentVideo=courcevideo)
                    courceContent.save()
                    return JsonResponse({'success': 'CourceContent added successfully'})
                except Exception as e:
                    return JsonResponse({'error': 'CourceContent not added'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    if request.method == 'DELETE':
       courceContentId = request.GET.get('courceContentId', None)
       if courceContentId:
            courceContent = CourceContent.objects.get(id=courceContentId)

            courceContent.delete()
            return JsonResponse({'success': 'CourceContent deleted successfully'})
       else:
           return JsonResponse({'error': 'No courceContent ID provided'}, status=400)     
    return render(request, 'manage-coursecontent.html')

@login_required(login_url='signin/')
def getSlotsData(request):
    # slotsId = request.GET.get('slotId', None)
    courseId = request.GET.get('courseId', None)
    bookingType = request.GET.get('bookingType', None)
    course = Cource.objects.filter(id=courseId).first()
    if course:
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
                        'slotPreBooked': i.slotPreBooked
                    })
        if bookingType == 'Pre-Booking':
            slots =  Slot.objects.filter(vehicle=course.vehicle).all()
            # print(slots)
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

        return JsonResponse(slotData,safe=False)
    
    return JsonResponse({'error': 'No slots found for this course'}, status=404)

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
    if id:
        try:
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
            return JsonResponse(attendanceData,safe=False)
        except Attendance.DoesNotExist:
            return JsonResponse({'error': 'Attendance not found'}, status=404)
    
    else:
        try:
            

            student = Student.objects.all()
            student = student.filter(id__in=Attendance.objects.all().values_list('student', flat=True))
            if VehicleName:
                student = student.filter(instructor__instructorVehicle__vehicleName=VehicleName)
            if branch:
                student = student.filter(Branch__branchName=branch)
            # student  = student.filter(student = Attendance.objects.all())
            studentData = []
            for i in student:
                if i.courceEndDate > datetime.today().date():
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
            return JsonResponse(studentData,safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
@csrf_exempt
@login_required(login_url='signin/')
def manageAttendance(request):
    if request.method == 'POST':
        attendanceId = request.POST.get('attendanceId',None)
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
                    attendance.student = Student.objects.get(id=student)
                    attendance.date = date
                    attendance.timeIn = inTime
                    attendance.timeOut = outTime
                    attendance.status = status
                    attendance.save()
                    student = Student.objects.get(id=student)
                    student.attened_session = int(student.attened_session) + int(sessionCount)
                    print("sa",student.attened_session)
                    student.save()
                    return JsonResponse({'success': 'Attendance updated successfully'})
                except Exception as e:
                    return JsonResponse({'error': 'Attendance not updated'}, status=404)
            else:
                try:
                    attendance = Attendance(student=Student.objects.get(id=student),date=date,timeIn=inTime,timeOut=outTime,status=status)
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
    users = UserProfile.objects.all()
    userData = []
    for i in users:
        data = {
            'id': i.id,
            'Name': i.user.first_name,
        }
        userData.append(data)
    return JsonResponse(userData,safe=False)
@login_required(login_url='signin/')
def getDlInfoData(request):
    dlinfo = request.GET.get('dlId', None)
    if dlinfo:
        try:
            dlinfo = DLInfo.objects.get(id=dlinfo)
            data = {
                'id': dlinfo.id,
                'Name': dlinfo.dlUser.user.first_name,
                'userID': dlinfo.dlUser.id,
                'dlNo': dlinfo.dlNo,
                'dlIssueDate': dlinfo.dlIssueDate,
                'dlExpiry': dlinfo.dlExpiry,
                'dlType': dlinfo.dlType,
            }
            return JsonResponse(data,safe=False)
        except DLInfo.DoesNotExist:
            return JsonResponse({'error': 'DlInfo not found'}, status=404)
    
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
    return JsonResponse(dlInfoData,safe=False)

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
                try:
                    dlinfo = DLInfo.objects.get(id=dlId)
                    dlinfo.dlNo = dlNo 
                    dlinfo.dlIssueDate = dlIssueDate
                    dlinfo.dlExpiry = dlExpiry
                    dlinfo.dlType = dlType
                    dlinfo.dlUser = UserProfile.objects.get(id=dlUser)
                    dlinfo.save()
                    return JsonResponse({'success': 'DlInfo updated successfully'})
                except Exception as e:
                    return JsonResponse({'error': 'DlInfo not updated'}, status=404)
            else:
                try:
                    dlUser = UserProfile.objects.get(id=dlUser)
                    dlinfo = DLInfo(dlNo=dlNo,dlIssueDate=dlIssueDate,dlExpiry=dlExpiry,dlType=dlType,dlUser=dlUser)
                    dlinfo.save()
                    return JsonResponse({'success': 'DlInfo added successfully'})
                except Exception as e:
                    if "UNIQUE constraint failed" in str(e): #check for unique constraint violation.
                        return JsonResponse({'error': 'DlInfo already Exists'}, status=400)
                    return JsonResponse({'error': 'DlInfo not added'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
    if request.method == 'DELETE':
        dlId = request.GET.get('dlId', None)
        try:
            if dlId:
                dlinfo = DLInfo.objects.get(id=dlId)
                dlinfo.delete()
                return JsonResponse({'success': 'DlInfo deleted successfully'})
            else:
                return JsonResponse({'error': 'No DlInfo ID provided'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
    return render(request, 'manage-DlInfo.html')

@login_required(login_url='signin/')
def getPaymentData(request):
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
    return JsonResponse(paymentData,safe=False)
@login_required(login_url='signin/')
def managePayment(request):
    if request.method == 'POST':
        paymentId = request.POST.get('paymentId',None)
        paymentAmount = request.POST.get('paymentReceived')
        paymentDate = request.POST.get('paymentDate')
        paymentBy = request.POST.get('paymentReceivedBy')
        paymentMode = request.POST.get('paymentMethod')
        studentId = request.POST.get('studentId')

        if paymentId:
            payment = Payment.objects.get(id=paymentId)
            payment.paymentAmount = paymentAmount
            payment.paymentDate = paymentDate
            payment.paymentRecevedBy = UserProfile.objects.get(id=paymentBy)
            payment.paymentMethod = paymentMode
            payment.save()
            student =  Student.objects.get(id=studentId)
            student.amountPaid = student.amountPaid + int(paymentAmount)
            student.amountPending = student.amountPending - int(paymentAmount)
            student.save()
            return JsonResponse({'success': 'Payment updated successfully'})
        else:
            payment =  Payment(student = Student.objects.get(id=studentId),paymentAmount=paymentAmount,paymentDate=paymentDate,paymentRecevedBy=UserProfile.objects.get(id=paymentBy),paymentMethod=paymentMode)
            payment.save()
            student =  Student.objects.get(id=studentId)
            student.amountPaid = student.amountPaid + int(paymentAmount)
            student.amountPending = student.amountPending - int(paymentAmount)
            student.save()
            
            return JsonResponse({'success': 'Payment added successfully'})
        
@login_required(login_url='signin/')
def getAddOnServiceData(request):
    addOnServiceId = request.GET.get('serviceId', None)
    if addOnServiceId:
        addOnService = AddOnService.objects.get(id=addOnServiceId)
        data = {
            'id': addOnService.id,
            'addOnServiceName': addOnService.serviceName,
            'addOnServiceAmount': addOnService.serviceFee,
            'mandetory': addOnService.mandetory,
        }
        return JsonResponse(data,safe=False)
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
        return JsonResponse(addOnServiceData,safe=False)
    
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

        if addOnServiceId:
            try:
                addOnService = AddOnService.objects.get(id=addOnServiceId)
                addOnService.serviceName = addOnServiceName
                addOnService.serviceFee = addOnServiceAmount
                addOnService.mandetory = mandetory
                addOnService.save()
                return JsonResponse({'success': 'Add On Service updated successfully'})
            except Exception as e:
                return JsonResponse({'error': 'Add On Service not updated'}, status=404)
        else:
            try:
                addOnService = AddOnService(serviceName=addOnServiceName,serviceFee=addOnServiceAmount,mandetory=mandetory)
                addOnService.save()
            except Exception as e:
                return JsonResponse({'error': 'Add On Service not added'}, status=404)
            
            return JsonResponse({'success': 'Add On Service added successfully'})
    

    if request.method == 'DELETE':
        addOnServiceId = request.GET.get('serviceId', None)
        try:
            if addOnServiceId:
                addOnService = AddOnService.objects.get(id=addOnServiceId)
                addOnService.delete()
                return JsonResponse({'success': 'Add On Service deleted successfully'})
            else:
                return JsonResponse({'error': 'No Add On Service ID provided'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
@login_required(login_url='signin/')
def getNotificationData(request):

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
    return JsonResponse(notificationData,safe=False)

@csrf_exempt
@login_required(login_url='signin/')
def manageNotification(request):
    if request.method == 'POST':
        notificationId = request.POST.get('notificationId',None)
        if notificationId:
            try:
                notification = Notification.objects.get(id=notificationId)
                notification.notificationIsRead = True
                notification.save()
                return JsonResponse({'success': 'Notification updated successfully'})
            except Exception as e:
                return JsonResponse({'error': 'Notification not updated'}, status=404)

            

    

    if request.method == 'DELETE':
        notificationId = request.GET.get('notificationId', None)
        try:
            if notificationId:
                notification = Notification.objects.get(id=notificationId)
                notification.delete()
                return JsonResponse({'success': 'Notification deleted successfully'})
            else:
                return JsonResponse({'error': 'No Notification ID provided'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)