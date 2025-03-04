from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import datetime

from AdminPanel.models import UserProfile, Branch, Slot, Cource, Student, Attendance, Complain, CourceContent
# Create your views here.

def getIndexData(request):   
    student = Student.objects.get(user__user=request.user)
    studentData = {
                "id":student.id,
                "name":student.user.user.first_name,
                "DOB":student.dob,
                "address":student.address,
                "Profilepic":student.user.profilePic,
                "cource":student.cource.courceName,
                "enrollmentDate":student.courceEnrollDate,
                "completionDate":student.courceEndDate,
                "vehicle":student.cource.courceInstructor.instructorVehicle.vehicleName,
                "instructor":student.instructor.user.user.first_name,
                "phone":student.user.phoneNo,
                "dlNo":student.Dlinfo.dlNo,
                "dlIssueDate":student.Dlinfo.dlIssueDate,
                "dlExpiry":student.Dlinfo.dlExpiry,
            }
    return JsonResponse(studentData,safe=False)

def index(request):
    
    
    
    return render(request, 'student/index.html')


def manage_complaints(request):
    return render(request, 'student/manage_complaints.html')


def manage_course(request):
    return render(request, 'student/course-details.html')