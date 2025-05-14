from django.shortcuts import render

# Create your views here.

from AdminPanel.models import (DLInfo,Instructor,Vehicle,Cource,Student,Attendance,Branch,UserProfile,Complain,CourceContent,Slot,Payment,AddOnService)
def index(request):
    return render(request, 'BranchAdmin/index.html')



