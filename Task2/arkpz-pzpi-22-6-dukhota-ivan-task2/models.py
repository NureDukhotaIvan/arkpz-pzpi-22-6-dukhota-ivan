# main/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('staff', 'Staff'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    email = models.EmailField(unique=True, null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['role']

    def __str__(self):
        return self.username

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    student_class = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='parents')

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Parent of {self.student})"

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    hire_date = models.DateField()
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    attendance_status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.position}"
    
class Sensor(models.Model):
    SENSOR_TYPES = (
        ('fire', 'Fire'),
        ('intrusion', 'Intrusion'),
        ('smoke', 'Smoke'),
    )
    type = models.CharField(max_length=50, choices=SENSOR_TYPES)
    location = models.CharField(max_length=255)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.type.capitalize()} Sensor at {self.location}"

class Camera(models.Model):
    location = models.CharField(max_length=255)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"Camera at {self.location}"

class Incident(models.Model):
    INCIDENT_TYPES = (
        ('fire', 'Fire'),
        ('intrusion', 'Intrusion'),
        ('smoke', 'Smoke'),
    )
    type = models.CharField(max_length=50, choices=INCIDENT_TYPES)
    description = models.TextField()
    severity = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])  
    date = models.DateTimeField(auto_now_add=True)
    sensor = models.ForeignKey(Sensor, on_delete=models.SET_NULL, null=True, blank=True, related_name='incidents')
    camera = models.ForeignKey(Camera, on_delete=models.SET_NULL, null=True, blank=True, related_name='incidents')
    report = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.type.capitalize()} Incident on {self.date.strftime('%Y-%m-%d %H:%M:%S')}"

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    attendance_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Attendance for {self.student} on {self.attendance_date}: {self.status}"

class Notification(models.Model):
    MESSAGE_TYPES = (
        ('incident', 'Incident'),
        ('attendance', 'Attendance'),
    )
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)

    def __str__(self):
        return f"Notification on {self.date.strftime('%Y-%m-%d %H:%M:%S')}"

