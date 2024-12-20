
# api/urls.py

from django.urls import path, include
from rest_framework import routers
from .views import (
    UserViewSet, StudentViewSet, ParentViewSet,
    StaffViewSet, SensorViewSet, CameraViewSet,
    IncidentViewSet, AttendanceViewSet, NotificationViewSet,
    RegisterView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'students', StudentViewSet)
router.register(r'parents', ParentViewSet)
router.register(r'staff', StaffViewSet)
router.register(r'sensors', SensorViewSet)
router.register(r'cameras', CameraViewSet)
router.register(r'incidents', IncidentViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'), 
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  
    path('', include(router.urls)),
]
