from django.contrib import admin
from django.urls import path, include
from .views import dashboard
from clients.views import client_create, client_detail, client_list, client_update, client_delete

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('projects/', include('projects.urls')),
    path('clients/', include('clients.urls')),
    path('tasks/', include('tasks.urls')),
]
