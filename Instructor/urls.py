from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('',views.index, name='index'),
    path('getIndexData/',views.getIndexData, name='getIndexData'),
    path('takeAttendance/',views.takeAttendance, name='takeAttendance'),
    path('getReamainingPaymentData/',views.getReamainingPaymentData, name='getReamainingPaymentData'),

]
