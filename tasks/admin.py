from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'status', 'deadline')
    search_fields = ('name', 'project__name')
    list_filter = ('status', 'deadline')