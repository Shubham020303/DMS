from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from datetime import time
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phoneNo = models.CharField(max_length=10)
    bloodGroup = models.CharField(max_length=5,blank=True,null=True)
    profilePic = models.ImageField(upload_to='profilePics/', null=True, blank=True)
    is_instructor = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_branchAdmin = models.BooleanField(default=False)
    is_superAdmin = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
class Branch(models.Model):
    branchName = models.CharField(max_length=50)
    branchAddress = models.TextField()
    branchPhoneNo = models.CharField(max_length=10)
    branchEmail = models.EmailField()
    branchIncharge = models.OneToOneField(UserProfile, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.branchName

class Slot(models.Model):
    slotName = models.CharField(max_length=50)
    slotStart = models.TimeField()
    slotEnd = models.TimeField()
    slotBranch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    def __str__(self):
        return self.slotName


# Create your models here.


class DLInfo(models.Model):
    dlNo = models.CharField(max_length=20)
    dlIssueDate = models.DateField()
    dlExpiry = models.DateField()
    dlUser = models.OneToOneField(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.dlNo + ' - ' + self.dlUser.user.first_name
    
class Vehicle(models.Model):
    vehicleName = models.CharField(max_length=50,blank=True,null=True)
    vehicleType = models.CharField(max_length=50,blank=True,null=True)
    vehicleNo = models.CharField(max_length=20,unique=True)
    insuranceValidity = models.DateField()
    pollutionValidity = models.DateField()
    fitnessValidity = models.DateField()



    def __str__(self):
        return self.vehicleNo
    
class Instructor(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE,null=True,blank=True,related_name='instructor')
    instructorVehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE,null=True,blank=True)
    instructorBranch = models.ForeignKey(Branch, on_delete=models.CASCADE,null=True,blank=True)
    
    def __str__(self):
        return self.user.user.first_name





class Cource(models.Model):
    courceName = models.CharField(max_length=50)
    courceDescription = models.TextField(null=True,blank=True)
    courceDuration = models.IntegerField()
    courceFee = models.IntegerField()
    courceInstructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    
    Branch = models.ForeignKey(Branch, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.courceName

class Student(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    applicationNo = models.CharField(max_length=10)
    dob = models.DateField()
    address = models.TextField()
    gender = models.CharField(max_length=10)
    
    Dlinfo = models.OneToOneField(DLInfo, on_delete=models.CASCADE)
    cource = models.ForeignKey(Cource, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE,null=True,blank=True,related_name='slot')
    Branch = models.ForeignKey(Branch, on_delete=models.CASCADE,null=True)
    courceEnrollDate = models.DateField(null=True,blank=True)
    courceEndDate = models.DateField(null=True,blank=True)
    courceStatus = models.BooleanField(default=False)
    def __str__(self):
        return self.user.user.first_name



class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    present = models.BooleanField(default=False)
    timeIn = models.TimeField(default=time(0, 0))
    timeOut = models.TimeField(default=time(0, 0))
    qr_code_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
  
    
    


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

    def __str__(self):
        return self.compalainFor.user.first_name + ' - ' + self.compalainTitle