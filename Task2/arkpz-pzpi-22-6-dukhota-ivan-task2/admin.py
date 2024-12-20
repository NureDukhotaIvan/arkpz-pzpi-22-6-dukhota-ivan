from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Student, Parent, Staff, Sensor,
    Camera, Incident, Attendance, Notification
)

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Roles', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Contact info', {'fields': ('email',)}),  
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'role', 'email', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'role', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('username',)

admin.site.register(User, UserAdmin)
admin.site.register(Student)
admin.site.register(Parent)
admin.site.register(Staff)
admin.site.register(Sensor)
admin.site.register(Camera)
admin.site.register(Incident)
admin.site.register(Attendance)
admin.site.register(Notification)

