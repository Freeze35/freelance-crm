from django.urls import path
from .views import task_create, task_update,task_detail

app_name = 'tasks'

urlpatterns = [
    path('projects/<int:project_id>/tasks/add/', task_create, name='create'),
    path('tasks/<int:task_id>/update/', task_update, name='update'),
    path('tasks/<int:pk>/', task_detail, name='detail'),
]