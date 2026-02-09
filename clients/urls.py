from django.urls import path
from .views import (
    client_list,
    client_create,
    client_detail,
    client_update,
    client_delete,
)

app_name = 'clients'

urlpatterns = [
    path('', client_list, name='list'),
    path('add/', client_create, name='create'),
    path('<int:pk>/', client_detail, name='detail'),
    path('<int:pk>/update/', client_update, name='update'),
    path('<int:pk>/delete/', client_delete, name='delete'),
]