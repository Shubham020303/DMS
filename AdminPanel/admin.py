from django.contrib import admin
from .models import (DLInfo,Instructor,Vehicle,Cource,Student,Attendance,Branch,UserProfile,Slot,Complain,CourceContent,Payment,AddOnService,Notification)
# Register your models here.
class slotAdmin(admin.ModelAdmin):
    list_display = ['slotName','slotStart','slotEnd','slotBranch']
    list_filter = ['slotBranch']
    search_fields = ['slotName','slotBranch']
    list_per_page = 10
# admin.site.register(User)
admin.site.register(DLInfo)
admin.site.register(Instructor)
admin.site.register(Vehicle)
admin.site.register(Cource)
admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(Branch)
admin.site.register(UserProfile)
admin.site.register(Slot,slotAdmin)
admin.site.register(Complain)
admin.site.register(CourceContent)
admin.site.register(Payment)
admin.site.register(AddOnService)
admin.site.register(Notification)