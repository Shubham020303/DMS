from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('',views.index, name='index'),
    path('instructor_signin/', views.instructor_signin, name='instructor_signin'),
    path('signout/', views.signout, name='signout'),
    path('getIndexData/',views.getIndexData, name='getIndexData'),
    path('takeAttendance/',views.takeAttendance, name='takeAttendance'),
    path('getReamainingPaymentData/',views.getReamainingPaymentData, name='getReamainingPaymentData'),

]
