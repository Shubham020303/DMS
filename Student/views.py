from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import datetime

from AdminPanel.models import UserProfile, Branch, Slot, Cource, Student, Attendance, Complain, CourceContent,DLInfo
# Create your views here.



def index(request):
    student = Student.objects.get(user__user=request.user)
    # dlinfo = DLInfo.objects.get(dlUser = student.user)


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
                # "DlNo":dlinfo.dlNo,
                # "DlIssueDate":dlinfo.dlIssueDate.strftime('%d/%m/%Y') if student.paymentDueDate else '',
                # "DlExpiry":dlinfo.dlExpiry.strftime('%d/%m/%Y') if student.paymentDueDate else '',
                # "DlType":dlinfo.dlType

            }
    
    return render(request, 'student/index.html',context=studentData)


def manage_complaints(request):
    return render(request, 'student/student-complains.html')


def manage_course(request):
    return render(request, 'student/course-details.html')