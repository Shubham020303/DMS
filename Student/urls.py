from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('',views.index, name='index'),
    path('student_signin/', views.student_signin, name='student_signin'),
    path('manage-complain/',views.manage_complaints, name='manage_complaints'),
    path('manage-attendance/',views.manage_attendance, name='manage_attendance'),
    path('manage-course/',views.manage_course, name='manage_course'),
    path('scan-qr/', views.scan_qr, name='scan_qr')


]