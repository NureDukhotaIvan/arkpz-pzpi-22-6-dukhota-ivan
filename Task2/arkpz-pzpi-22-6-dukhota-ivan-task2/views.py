# api/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from main.models import (
    User, Student, Parent, Staff, Sensor,
    Camera, Incident, Attendance, Notification
)
from .serializers import (
    UserSerializer, StudentSerializer, ParentSerializer,
    StaffSerializer, SensorSerializer, CameraSerializer,
    IncidentSerializer, AttendanceSerializer, NotificationSerializer
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import IsAdmin, IsStaff, IsParent, IsStudent, IsAdminOrStaff
from rest_framework import generics
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_fields = ['student_class', 'last_name']
    search_fields = ['first_name', 'last_name']

class ParentViewSet(viewsets.ModelViewSet):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_fields = ['last_name']
    search_fields = ['first_name', 'last_name']

class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrStaff]
    filterset_fields = ['position', 'last_name']
    search_fields = ['first_name', 'last_name']

class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['type', 'location', 'status']
    search_fields = ['location']

class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['location', 'status']
    search_fields = ['location']

class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_fields = ['type', 'severity', 'sensor', 'camera', 'report']
    search_fields = ['description']

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_fields = ['student', 'attendance_date', 'status']
    search_fields = ['student__first_name', 'student__last_name']

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_fields = ['incident', 'parent', 'staff']
    search_fields = ['message']

