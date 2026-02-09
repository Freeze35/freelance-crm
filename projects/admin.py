from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'status', 'budget', 'deadline')
    search_fields = ('name', 'client__name')
    list_filter = ('status', 'deadline')