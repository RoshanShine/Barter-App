from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class NoLogMixin:
    """Mixin to disable admin logging because LogEntry fails with MongoDB ObjectIds"""
    def log_addition(self, *args, **kwargs): pass
    def log_change(self, *args, **kwargs): pass
    def log_deletion(self, *args, **kwargs): pass

@admin.register(CustomUser)
class CustomUserAdmin(NoLogMixin, UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    ordering = ('username',)
