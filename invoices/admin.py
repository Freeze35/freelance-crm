from django.contrib import admin
from .models import Invoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'project', 'amount', 'status', 'due_date')
    search_fields = ('number', 'project__name')
    list_filter = ('status', 'due_date')