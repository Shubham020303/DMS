from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'student/index.html')


def manage_complaints(request):
    return render(request, 'student/manage_complaints.html')


def manage_course(request):
    return render(request, 'student/course-details.html')