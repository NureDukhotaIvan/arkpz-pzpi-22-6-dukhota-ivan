# api/serializers.py

from rest_framework import serializers
from main.models import (
    User, Student, Parent, Staff, Sensor,
    Camera, Incident, Attendance, Notification
)




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'email']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'password', 'role', 'email']

    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.pop('email', None)
        user = User(**validated_data)
        if email:
            user.email = email
        user.set_password(password)
        user.save()
        return user

class StudentSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()

    class Meta:
        model = Student
        fields = ['id', 'user', 'first_name', 'last_name', 'date_of_birth', 'student_class']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserCreateSerializer.create(UserCreateSerializer(), validated_data=user_data)
        student = Student.objects.create(user=user, **validated_data)
        return student

class ParentSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())

    class Meta:
        model = Parent
        fields = ['id', 'user', 'first_name', 'last_name', 'email', 'phone', 'student']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        student = validated_data.pop('student')
        user = UserCreateSerializer.create(UserCreateSerializer(), validated_data=user_data)
        parent = Parent.objects.create(user=user, student=student, **validated_data)
        return parent

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        student = validated_data.pop('student', instance.student)
        user = instance.user

        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        instance.student = student
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

class StaffSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()

    class Meta:
        model = Staff
        fields = ['id', 'user', 'first_name', 'last_name', 'position', 'hire_date', 'email', 'phone', 'attendance_status']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserCreateSerializer.create(UserCreateSerializer(), validated_data=user_data)
        staff = Staff.objects.create(user=user, **validated_data)
        return staff

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user

        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ['id', 'type', 'location', 'status']

class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ['id', 'location', 'status']

class IncidentSerializer(serializers.ModelSerializer):
    sensor = SensorSerializer(read_only=True)
    camera = CameraSerializer(read_only=True)
    sensor_id = serializers.PrimaryKeyRelatedField(
        queryset=Sensor.objects.all(), source='sensor', write_only=True, required=False, allow_null=True
    )
    camera_id = serializers.PrimaryKeyRelatedField(
        queryset=Camera.objects.all(), source='camera', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Incident
        fields = [
            'id', 'type', 'description', 'severity', 'date',
            'sensor', 'sensor_id', 'camera', 'camera_id', 'report'
        ]

class AttendanceSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), source='student', write_only=True
    )

    class Meta:
        model = Attendance
        fields = ['id', 'student', 'student_id', 'attendance_date', 'status']

class NotificationSerializer(serializers.ModelSerializer):
    incident = IncidentSerializer(read_only=True)
    incident_id = serializers.PrimaryKeyRelatedField(
        queryset=Incident.objects.all(), source='incident', write_only=True, required=False, allow_null=True
    )
    parent = ParentSerializer(read_only=True)
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Parent.objects.all(), source='parent', write_only=True, required=False, allow_null=True
    )
    staff = StaffSerializer(read_only=True)
    staff_id = serializers.PrimaryKeyRelatedField(
        queryset=Staff.objects.all(), source='staff', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Notification
        fields = [
            'id', 'message', 'date',
            'incident', 'incident_id',
            'parent', 'parent_id',
            'staff', 'staff_id',
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=True)

    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False)
    student_class = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False, allow_blank=True)
    position = serializers.CharField(required=False, allow_blank=True)
    hire_date = serializers.DateField(required=False)
    attendance_status = serializers.BooleanField(required=False)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), required=False)

    class Meta:
        model = User
        fields = [
            'username', 'password', 'role',
            'first_name', 'last_name', 'date_of_birth', 'student_class',
            'email', 'phone', 'position', 'hire_date', 'attendance_status',
            'student'
        ]

    def create(self, validated_data):
        role = validated_data.pop('role')
        password = validated_data.pop('password')
        email = validated_data.pop('email', None)

        user = User.objects.create(username=validated_data['username'], role=role, email=email)
        user.set_password(password)
        user.save()

        if role == 'student':
            Student.objects.create(
                user=user,
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
                date_of_birth=validated_data.get('date_of_birth', '2000-01-01'),
                student_class=validated_data.get('student_class', '')
            )
        elif role == 'parent':
            student = validated_data.get('student')
            if not student:
                raise serializers.ValidationError({"student": "This field is required for parents."})
            Parent.objects.create(
                user=user,
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
                email=validated_data.get('email', ''),
                phone=validated_data.get('phone', ''),
                student=student
            )
        elif role == 'staff':
            Staff.objects.create(
                user=user,
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
                position=validated_data.get('position', ''),
                hire_date=validated_data.get('hire_date', '2020-01-01'),
                email=validated_data.get('email', ''),
                phone=validated_data.get('phone', ''),
                attendance_status=validated_data.get('attendance_status', True)
            )

        return user


class IncidentStatisticsSerializer(serializers.Serializer):
    total_incidents = serializers.IntegerField()
    average_severity = serializers.FloatField()


class SecurityEffectivenessSerializer(serializers.Serializer):
    security_effectiveness_index = serializers.FloatField()
    details = serializers.DictField()
