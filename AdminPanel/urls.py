from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.index, name='index/'),
    path('getUserProfileData/', views.getUserProfileData, name='getUserProfileData/'),
    path('getReamainingPaymentData/', views.getReamainingPaymentData, name='getReamainingPaymentData/'),
    path('getSlotWiseData/', views.getSlotWiseData, name='getSlotWiseData/'),
    path('getEearningData/', views.getEearningData, name='getEearningData/'),
    path('getInstructorData/', views.getInstructorData, name='getInstructorData/'),
    path('manage-instructor/', views.manage_instructor, name='manage-instructor/'),
    path('getStudentData/', views.getStudentData, name='getStudentData/'),
    path('manage-student/', views.manage_student, name='manage-student/'),
    path('getBranchData/', views.getBranchData, name='getBranchData/'),
    path('getBranchAdminData/', views.getBranchAdminData, name='getBranchAdminData/'),
    path('manage-branch/', views.manage_branch, name='manage-branch/'),
    path('getVehicleData/', views.getVehicleData, name='getVehicleData/'),
    path('manage-vehicle/', views.manage_vehicle, name='manage-vehicle/'),
    path('manage-slot/', views.manage_slot, name='manage-slot/'),
    path('getCourseData/', views.getCourseData, name='getCourseData/'),
    path('manage-course/', views.manage_course, name='manage-course/'),
    path('getComplainData/', views.getComplainData, name='getComplainData/'),
    path('manage-complain/', views.manage_complain, name='manage-complain/'),
    path('getcourceContentData/', views.getcourceContentData, name='getcourceContentData/'),
    path('manage-coursecontent/', views.manageCourseContent, name='manage-coursecontent/'),
    path('getSlotsData/',views.getSlotsData,name='getSlotsData/'),
    path('manage-slots/', views.manageSlots, name='manage-slots/'),
    path('manage-attendance/', views.manageAttendance, name='manage-attendance/'),
    path('getAttendanceData/', views.getAttendanceData, name='getAttendanceData/'),
    path('manage-DlInfo/', views.manageDlInfo, name='manage-DlInfo/'),
    path('getDlInfoData/', views.getDlInfoData, name='getDlInfoData/'),
    path('getPaymentData/', views.getPaymentData, name='getPaymentData/'),
    path('manage-payment/', views.managePayment, name='manage-payment/'),
    # path('DeleteALlComplain/', views.DeleteALlComplain, name='DeleteALlComplain/'),
    
    # path('getVehicleData/', views.getVehicleData, name='getVehicleData/'),
    # path('manage-vehicle/', views.manage_vehicle, name='manage-vehicle/'),
    # path('course/', views.course, name='course/'),
]
urlpatterns += static(settings.MEDIA_URL, 
    document_root=settings.MEDIA_ROOT)
