from django.urls import path
from .views import task_create,task_detail,task_update,task_delete

app_name = 'tasks'

urlpatterns = [
    path('projects/<int:project_id>/tasks/add/', task_create, name='create'),
    path('tasks/<int:pk>/update/', task_update, name='update'),
    path('tasks/<int:pk>/', task_detail, name='detail'),
    path('tasks/<int:pk>/delete/', task_delete, name='delete'),
]