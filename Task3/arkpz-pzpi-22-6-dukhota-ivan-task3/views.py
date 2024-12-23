# api/views.py

from rest_framework import viewsets, generics, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from main.models import (
    User, Student, Parent, Staff, Sensor,
    Camera, Incident, Attendance, Notification
)
from .serializers import (
    UserSerializer, StudentSerializer, ParentSerializer,
    StaffSerializer, SensorSerializer, CameraSerializer,
    IncidentSerializer, AttendanceSerializer, NotificationSerializer,
    IncidentStatisticsSerializer, RegisterSerializer, SecurityEffectivenessSerializer
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import IsAdmin, IsStaff, IsParent, IsStudent, IsAdminOrStaff, IsStaffUser
from rest_framework.views import APIView  
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg
from django.conf import settings
from datetime import datetime
import os
import psycopg
from psycopg import sql
from django.core.management import call_command
import subprocess


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('username')  
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['username', 'email']
    ordering = ['username']

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all().order_by('last_name', 'first_name')  
    serializer_class = StudentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_fields = ['student_class', 'last_name']
    search_fields = ['first_name', 'last_name']
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['first_name', 'last_name', 'student_class']
    ordering = ['last_name', 'first_name']

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
    queryset = Sensor.objects.all().order_by('type', 'location') 
    serializer_class = SensorSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsStaffUser]  
    filterset_fields = ['type', 'location', 'status']
    search_fields = ['location']
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['type', 'location', 'status']
    ordering = ['type', 'location']

class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.all().order_by('location') 
    serializer_class = CameraSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsStaffUser] 
    filterset_fields = ['location', 'status']
    search_fields = ['location']
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['location', 'status']
    ordering = ['location']

class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all().order_by('date') 
    serializer_class = IncidentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsStaffUser]  
    filterset_fields = ['type', 'severity', 'sensor', 'camera', 'report']
    search_fields = ['description']
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['type', 'severity', 'date', 'sensor', 'camera', 'report']
    ordering = ['date']

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all().order_by('attendance_date')  
    serializer_class = AttendanceSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsStaffUser] 
    filterset_fields = ['student', 'attendance_date', 'status']
    search_fields = ['student__first_name', 'student__last_name']
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['student', 'attendance_date', 'status']
    ordering = ['attendance_date']

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by('date')  
    serializer_class = NotificationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsStaffUser] 
    filterset_fields = ['incident', 'parent', 'staff']
    search_fields = ['message']
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['incident', 'parent', 'staff', 'date']
    ordering = ['date']

class IncidentStatisticsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrStaff] 

    def get(self, request, format=None):

        total_incidents = Incident.objects.count()
        
        average_severity = Incident.objects.aggregate(Avg('severity'))['severity__avg']
        
        if average_severity is None:
            average_severity = 0.0
        
        average_severity = round(average_severity, 2)
        
        data = {
            'total_incidents': total_incidents,
            'average_severity': average_severity
        }
        
        serializer = IncidentStatisticsSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    



class SecurityEffectivenessView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsStaffUser] 

    def get(self, request, format=None):
        W1 = 0.2  # Сенсори
        W2 = 0.2  # Камери
        W3 = 0.2  # Інциденти
        W4 = 0.2  # Рівень присутності
        W5 = 0.2  # Severity інцидентів

        total_sensors = Sensor.objects.count()
        functional_sensors = Sensor.objects.filter(status=True).count()
        sensor_coverage = functional_sensors / total_sensors if total_sensors > 0 else 0

        total_cameras = Camera.objects.count()
        functional_cameras = Camera.objects.filter(status=True).count()
        camera_coverage = functional_cameras / total_cameras if total_cameras > 0 else 0

        incidents = Incident.objects.all()
        I_n = incidents.count()
        I_t = incidents.aggregate(Avg('severity'))['severity__avg'] or 1 

        incident_rate = 1 - (I_n / I_t) if I_t > 0 else 0

        total_students = Student.objects.count()
        total_attendance_records = Attendance.objects.count()
        attendance_rate = (total_attendance_records / (total_students * 30)) * 100 if total_students > 0 else 0  

        S_max = 5 
        S_avg_severity = incidents.aggregate(Avg('severity'))['severity__avg'] or 0
        severity_index = (S_max - S_avg_severity) / S_max

        SEI = (
            (sensor_coverage * W1) +
            (camera_coverage * W2) +
            (incident_rate * W3) +
            ((attendance_rate / 100) * W4) +
            (severity_index * W5)
        ) / (W1 + W2 + W3 + W4 + W5)

        SEI = round(SEI, 2)

        details = {
            'sensor_coverage': sensor_coverage,
            'camera_coverage': camera_coverage,
            'incident_rate': incident_rate,
            'attendance_rate': attendance_rate,
            'severity_index': severity_index,
        }

        data = {
            'security_effectiveness_index': SEI,
            'details': details
        }

        serializer = SecurityEffectivenessSerializer(instance=data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class PostgresDBManagementView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsStaffUser]

    def post(self, request, action):
        if action == 'migrate':
            return self.perform_migrations()
        elif action == 'backup':
            return self.create_backup()
        else:
            return Response(
                {'error': f'Invalid action: {action}. Use "migrate" or "backup".'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_migrations(self):
        try:
            call_command('makemigrations')
            call_command('migrate')
            return Response({'message': 'Migrations performed successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_backup(self):
        try:
            backup_dir = 'D:/backups' 
            os.makedirs(backup_dir, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(backup_dir, f'db_backup_{timestamp}.sql')

            db_settings = settings.DATABASES['default']
            db_name = db_settings['NAME']
            db_user = db_settings['USER']
            db_host = db_settings.get('HOST', 'localhost')
            db_port = db_settings.get('PORT', '5432')
            db_password = db_settings['PASSWORD']

            import subprocess

            dump_command = [
                'pg_dump',
                '-h', db_host,
                '-p', str(db_port),
                '-U', db_user,
                '-F', 'c',  
                '-b',       
                '-v',      
                '-f', backup_file,
                db_name
            ]

            env = os.environ.copy()
            env['PGPASSWORD'] = db_password

            result = subprocess.run(dump_command, env=env, capture_output=True, text=True)

            if result.returncode != 0:
                return Response({'error': result.stderr}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                'message': 'Backup created successfully.',
                'backup_file': backup_file
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
