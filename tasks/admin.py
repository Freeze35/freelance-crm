from django.contrib import admin
from .models import Task

from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'deadline', 'is_overdue')  # ← исправлено
    list_filter = ('status', 'project')
    search_fields = ('title', 'description')
    date_hierarchy = 'deadline'
    readonly_fields = ('created_at',)

    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Просрочена'