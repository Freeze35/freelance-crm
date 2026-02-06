from django.contrib import admin
from django.urls import path, include
from .views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('projects/', include('projects.urls')),
    path('clients/', include('clients.urls')),
    path('tasks/', include('tasks.urls')),
    path('invoices/', include('invoices.urls')),
]
