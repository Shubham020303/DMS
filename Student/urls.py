from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('',views.index, name='index'),
    path('signout/', views.student_signout, name='student_signout'),
    path('change-password/', views.change_password, name='change_password'),
    path('student_signin/', views.student_signin, name='student_signin'),
    path('getCourseContentData/', views.getCourseContentData, name='getCourseContentData'),
    path('getStudentComplaints/',views.get_student_complaints, name='get_student_complaints'),
    path('manage-complain/',views.manage_complaints, name='manage_complaints'),
    path('getStudentProfileData/', views.getStudentProfileData, name='getStudentProfileData'),
    path('getAllUserData/', views.getAllUserData, name='getAllUserData'),
    path('manage-attendance/',views.manage_attendance, name='manage_attendance'),
    path('manage-course/',views.manage_course, name='manage_course'),
    path('scan-qr/', views.scan_qr, name='scan_qr')


]