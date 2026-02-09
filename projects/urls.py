from django.urls import path
from .views import (
    project_list,
    project_create,
    project_detail,
    project_update,
    project_delete,
    overdue_tasks
)

app_name = 'projects'

urlpatterns = [
    path('', project_list, name='list'),
    path('add/', project_create, name='create'),
    path('<int:pk>/', project_detail, name='detail'),
    path('<int:pk>/update/', project_update, name='update'),
    path('<int:pk>/delete/', project_delete, name='delete'),
    path('overdue/', overdue_tasks, name='overdue_tasks'),
]
