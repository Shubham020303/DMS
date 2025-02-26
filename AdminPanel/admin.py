from django.contrib import admin
from .models import (DLInfo,Instructor,Vehicle,Cource,Student,Attendance,Branch,UserProfile,Slot,Complain,CourceContent)
# Register your models here.

# admin.site.register(User)
admin.site.register(DLInfo)
admin.site.register(Instructor)
admin.site.register(Vehicle)
admin.site.register(Cource)
admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(Branch)
admin.site.register(UserProfile)
admin.site.register(Slot)
admin.site.register(Complain)
admin.site.register(CourceContent)

