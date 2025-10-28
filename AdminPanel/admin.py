from django.contrib import admin
from .models import (DLInfo,Instructor,Vehicle,Cource,Student,Attendance,Branch,UserProfile,Slot,Complain,CourceContent,Payment,AddOnService,Notification,StudentCouseHistory)
# Register your models here.
class slotAdmin(admin.ModelAdmin):
    list_display = ['slotStart','slotEnd','slotBranch','vehicle']
    list_filter = ['slotBranch','vehicle']
    search_fields = ['slotBranch']
    list_per_page = 10

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user','phoneNo','is_instructor','is_student','is_branchAdmin','is_superAdmin','is_active']
    search_fields = ['user__username','phoneNo']
    list_per_page = 10

class VehicleAdmin(admin.ModelAdmin):
    list_display = ['vehicleName','vehicleType','vehicleNo','vehicleBranch','is_active']
    search_fields = ['vehicleName','vehicleType','vehicleNo']
    list_per_page = 10

class CourceAdmin(admin.ModelAdmin):
    list_display = ['courceName','vehicle','courceFee','courceDuration','is_active']
    search_fields = ['courceName','vehicle__vehicleName']
    list_per_page = 10

class StudentAdmin(admin.ModelAdmin):
    list_display = ['user','cource','instructor','dob','amountPending','is_active']
    search_fields = ['user__user__username','cource__courceName','instructor__user__user__username']
    list_filter = ['cource','instructor']
    list_per_page = 10

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student','paymentDate','paymentAmount','paymentMethod','paymentRecevedBy']
    search_fields = ['student__user__user__username','paymentMethod','paymentBranch__branchName']
    list_per_page = 10

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['notificationTitle','notificationDate','notificationBranch','notificationIsRead']
    search_fields = ['notificationTitle','notificationBranch']
    list_per_page = 10


class InstructorAdmin(admin.ModelAdmin):
    list_display = ['user','dob','instructorBranch','is_active']
    search_fields = ['user__user__username','instructorBranch__branchName']
    list_per_page = 10

class DlInfoAdmin(admin.ModelAdmin):
    list_display = ['dlNo','dlUser','dlIssueDate','dlExpiry','dlType']
    search_fields = ['dlUser__user__username','dlNo','dlType']
    list_per_page = 10

class BranchAdmin(admin.ModelAdmin):
    list_display = ['branchName','branchPhoneNo','branchEmail','branchIncharge','is_active']
    search_fields = ['branchName','branchIncharge__user__username']
    list_per_page = 10

class ComplainAdmin(admin.ModelAdmin):
    list_display = ['compalainTitle','compalainForm','compalainFor','complainResolved','complainBranch','resolved_by','created_at']
    search_fields = ['compalainTitle','compalainForm__user__username','compalainFor__user__username','complainBranch__branchName']
    list_filter = ['complainResolved','complainBranch']
    list_per_page = 10

class CourceContentAdmin(admin.ModelAdmin):
    list_display = ['contentDescription','contentVideo','contentFile']
    search_fields = ['contentDescription']
    list_per_page = 10

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student','date','timeIn','timeOut','status']
    search_fields = ['student__user__user__username','date','status']
    list_per_page = 10

class AddOnServiceAdmin(admin.ModelAdmin):
    list_display = ['serviceName','serviceFee','mandetory','is_active']
    search_fields = ['serviceName']
    list_per_page = 10
class  StudentCouseHistoryAdmin(admin.ModelAdmin):
    list_display = ['student','cource','instructor','courceEnrollDate','courceCompletionDate']
    search_fields = ['student__user__user__username','cource__courceName','instructor__user__user__username']
    list_filter = ['cource','instructor']
    list_per_page = 10
# admin.site.register(User)
admin.site.register(DLInfo,DlInfoAdmin)
admin.site.register(Instructor,InstructorAdmin)
admin.site.register(Vehicle,VehicleAdmin)
admin.site.register(Cource,CourceAdmin)
admin.site.register(Student,StudentAdmin)
admin.site.register(Attendance,AttendanceAdmin)
admin.site.register(Branch,BranchAdmin)
admin.site.register(UserProfile,UserProfileAdmin)
admin.site.register(Slot,slotAdmin)
admin.site.register(Complain,ComplainAdmin)
admin.site.register(CourceContent,CourceContentAdmin)
admin.site.register(Payment,PaymentAdmin)
admin.site.register(AddOnService,AddOnServiceAdmin)
admin.site.register(Notification,NotificationAdmin)
admin.site.register(StudentCouseHistory,StudentCouseHistoryAdmin)