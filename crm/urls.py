from django.contrib import admin
from django.urls import path
from .views import dashboard
from clients.views import client_create, client_detail, client_list, client_update, client_delete

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('clients/add/', client_create, name='client_create'),
    path('clients/', client_list, name='client_list'),
    path('clients/<int:pk>/', client_detail, name='client_detail'),
    path('clients/<int:pk>/update/', client_update, name='client_update'),
    path('clients/<int:pk>/delete/', client_delete, name='client_delete'),
]
