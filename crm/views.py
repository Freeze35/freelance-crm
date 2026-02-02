from django.shortcuts import render
from django.utils import timezone
from clients.models import Client
from projects.models import Project
from tasks.models import Task

def dashboard(request):
    client_count = Client.objects.count()

    # Total number of projects (excluding cancelled ones)
    project_total = Project.objects.exclude(status='canceled').count()

    # In progress
    project_in_progress = Project.objects.filter(status='in_progress').count()

    # Completed
    project_done = Project.objects.filter(status='done').count()

    # Overdue tasks
    overdue_tasks = Task.objects.filter(
        status__in=['todo', 'in_progress'],
        deadline__lt=timezone.now()
    ).count()

    context = {
        'client_count': client_count,
        'project_total': project_total,          # ← общее количество
        'project_in_progress': project_in_progress,
        'project_done': project_done,
        'overdue_tasks': overdue_tasks,
    }
    return render(request, 'dashboard.html', context)