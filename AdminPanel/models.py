from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from datetime import time,datetime
from django.db.models import F, Case, When, Value
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime,timedelta
import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phoneNo = models.CharField(max_length=10)
    bloodGroup = models.CharField(max_length=5,blank=True,null=True)
    profilePic = models.ImageField(upload_to='profilePics/', null=True, blank=True)
    is_instructor = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_branchAdmin = models.BooleanField(default=False)
    is_superAdmin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username
class Branch(models.Model):
    branchName = models.CharField(max_length=50)
    branchAddress = models.TextField()
    branchPhoneNo = models.CharField(max_length=10)
    branchEmail = models.EmailField()
    branchIncharge = models.OneToOneField(UserProfile, on_delete=models.CASCADE,null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.branchName

class Vehicle(models.Model):
    vehicleName = models.CharField(max_length=50,blank=True,null=True)
    vehicleType = models.CharField(max_length=50,blank=True,null=True)
    vehicleNo = models.CharField(max_length=20,unique=True)
    vehicleBranch = models.ForeignKey(Branch, on_delete=models.CASCADE,null=True,blank=True)
    insuranceValidity = models.DateField()
    pollutionValidity = models.DateField()
    fitnessValidity = models.DateField()
    qrCodeData = models.CharField(max_length=64,blank=True,null=True)
    qrCodeImage = models.ImageField(upload_to='vehicle_qrcodes/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
   


    def __str__(self):
        return self.vehicleNo

    def generate_qrcode(self):
        if not self.qrCodeData:
            self.qrCodeData = str(uuid.uuid4())
        qr = qrcode.make(self.qrCodeData)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        file_name = f'vehicle_qrcode_{self.vehicleNo}.png'
        self.qrCodeImage.save(file_name, ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        if not self.qrCodeData or not self.qrCodeImage:
            self.generate_qrcode()
        super().save(*args, **kwargs)

class Slot(models.Model):
    class Meta:
        unique_together = ('vehicle','slotStart', 'slotEnd', 'slotBranch')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE,null=True,blank=True)
    slotStart = models.TimeField()
    slotEnd = models.TimeField()
    slotBranch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    slotUsed = models.BooleanField(default=False)
    slotPreBooked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return str(self.slotStart) + ' - ' + str(self.slotEnd)


# Create your models here.
class AddOnService(models.Model):
    serviceName = models.CharField(max_length=50)
    serviceFee = models.IntegerField()
    mandetory = models.BooleanField(default=False) 
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.serviceName

class DLInfo(models.Model):
    choises = (
        ('Learning License', 'Learning License'),
        ('Driving License', 'Driving License'),
    )
    dlNo = models.CharField(max_length=20)
    dlIssueDate = models.DateField()
    dlExpiry = models.DateField()
    dlType = models.CharField(max_length=20,choices=choises,blank=True,null=True)
    dlUser = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.dlNo + ' - ' + self.dlUser.user.first_name
    

class Instructor(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE,null=True,blank=True,related_name='instructor')
    dob = models.DateField(blank=True,null=True)
    
    instructorBranch = models.ForeignKey(Branch, on_delete=models.CASCADE,null=True,blank=True)
    adharCard = models.FileField(upload_to='instructorDoc/',null=True,blank=True)
    aggreementDoc = models.FileField(upload_to='instructorDoc/',null=True,blank=True)
    policeVerificationDoc = models.FileField(upload_to='instructorDoc/',null=True,blank=True)
    is_active = models.BooleanField(default=True)    
    def __str__(self):
        return self.user.user.first_name





class Cource(models.Model):
    courceName = models.CharField(max_length=50)
    courceDescription = models.TextField(null=True,blank=True)
    courceDuration = models.IntegerField()
    courceFee = models.IntegerField()
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE,null=True,blank=True)
    total_session = models.IntegerField(default=0,null=True,blank=True)
    Branch = models.ForeignKey(Branch, on_delete=models.CASCADE,null=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.courceName

class Student(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    applicationNo = models.CharField(max_length=10)
    dob = models.DateField()
    address = models.TextField()
    gender = models.CharField(max_length=10)
    cource = models.ForeignKey(Cource, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE,null=True,blank=True,related_name='slot')
    Branch = models.ForeignKey(Branch, on_delete=models.CASCADE,null=True)
    booking_Type = models.CharField(max_length=20,null=True,blank=True)
    courceEnrollDate = models.DateField(null=True,blank=True)
    courceEndDate = models.DateField(null=True,blank=True)
    courceStatus = models.BooleanField(default=False)
    amountPaid = models.IntegerField(null=True,blank=True,default=0)
    amountPending = models.IntegerField(null=True,blank=True,default=0)
    paymentDueDate = models.DateField(null=True,blank=True)
    attened_session = models.IntegerField(default=0,null=True,blank=True)
    addOnService = models.ManyToManyField(AddOnService)
    student_staus = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.user.user.first_name

@receiver(post_save, sender=Student)
def update_slot_used(sender, instance, **kwargs):
    if instance.attened_session == instance.cource.total_session and instance.student_staus == True:
            instance.student_staus = False
            instance.save()
            student = Student.objects.filter(slot=instance.slot, student_staus=True)
            if len(student) == 0:
                instance.slot.slotUsed = False
                instance.slot.save()
            else:
                if instance.slot.slotPreBooked == True:
                    student = Student.objects.filter(slot=instance.slot, student_staus=True).last()
                    student.booking_Type = "Normal"
                    student.save()
                    instance.slot.slotUsed = True
                    instance.slot.slotPreBooked = False
                    instance.slot.save()
                else:
                    instance.slot.slotUsed = False
                    instance.slot.save()
   

class Attendance(models.Model):
    choices = (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Leave', 'Leave'),
    )
    class Meta:
        unique_together = ('student', 'date')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10,choices=choices,null=True,blank=True)
    timeIn = models.TimeField(null=True,blank=True)
    timeOut = models.TimeField(null=True,blank=True)
    
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.student.user.user.first_name + ' - ' + str(self.date)

# @receiver(post_save, sender=Attendance)
# def update_student_cource_end_date(sender, instance, **kwargs):
        
#         if instance.status == 'Leave':
#             print("ONLeave")
#             try:
#                 next_day = instance.date + timedelta(days=1)
#                 if next_day.weekday() == 6:
#                     next_day =  next_day + timedelta(days=1)
#                 student = Student.objects.get(id=instance.student.id)
#                 student.courceEndDate = next_day
#                 student.save()   
#             except Student.DoesNotExist:
#             # Log error if student doesn't exist
#                 print(f"Error: Student with ID {instance.student.id} not found")
#             except Exception as e:
#             # Catch any other exceptions
#                 print(f"Error updating student course end date: {e}") 
    


class CourceContent(models.Model):
    
    contentDescription = models.TextField()
    contentVideo = models.FileField(upload_to='courceContent/',null=True,blank=True)
    contentFile = models.FileField(upload_to='courceContent/',null=True,blank=True)

    def __str__(self):
        return self.contentDescription 


class Complain(models.Model):
    compalainForm = models.ForeignKey(Student, on_delete=models.CASCADE,null=True)
    compalainFor = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    compalainTitle = models.CharField(max_length=500,null=True,blank=True)
    complainDescription = models.TextField()
    complainDate = models.DateField()
    complainTime = models.TimeField(default=time(0, 0))
    complainResolved = models.BooleanField(default=False)
    complainBranch = models.ForeignKey(Branch, on_delete=models.CASCADE,null=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.compalainFor.user.first_name + ' - ' + self.compalainTitle
    
class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    paymentDate = models.DateField()
    paymentAmount = models.IntegerField()
    paymentMethod = models.CharField(max_length=50)
    paymentRecevedBy = models.ForeignKey(UserProfile, on_delete=models.CASCADE,null=True,blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.student.user.user.first_name
    

class Notification(models.Model):
    notificationTitle = models.CharField(max_length=100)
    notificationDate = models.DateField()
    notificationTime = models.TimeField(default=time(0, 0))
    notificationBranch = models.ForeignKey(Branch, on_delete=models.CASCADE,null=True)
    notificationIsRead = models.BooleanField(default=False)


    def __str__(self):
        return self.notificationTitle

