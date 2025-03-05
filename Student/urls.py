from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('',views.index, name='index'),

    path('manage-complaints/',views.manage_complaints, name='manage_complaints'),
    path('manage-course/',views.manage_course, name='manage_course'),


]