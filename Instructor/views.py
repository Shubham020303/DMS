from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from AdminPanel.models import (DLInfo,Instructor,Vehicle,Cource,Student,Attendance,Branch)
# Create your views here.
def index(request):
    ins =Instructor.objects.filter(user=request.user).first()
    context = {
        'user': request.user,
        'profilepic':ins.profilePic.url if ins else '',
    }
    return render(request, 'instructor/index.html')




