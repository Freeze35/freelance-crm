from django.shortcuts import render
from django.utils import timezone
from clients.models import Client
from projects.models import Project
from tasks.models import Task


def dashboard(request):
    client_count = Client.objects.count()

    # Counting projects by status
    # Excluding 'canceled' statuses so they don't become an eyesore in the overall statistics
    active_projects = Project.objects.exclude(status='canceled')

    project_total = active_projects.count()
    project_new = active_projects.filter(status='new').count()
    project_in_progress = active_projects.filter(status='in_progress').count()
    project_done = active_projects.filter(status='completed').count()

    overdue_tasks_count = Task.objects.filter(
        status__in=['todo', 'in_progress'],
        deadline__lt=timezone.now().date()
    ).count()

    context = {
        'client_count': client_count,
        'project_total': project_total,
        'project_new': project_new,
        'project_in_progress': project_in_progress,
        'project_done': project_done,
        'overdue_tasks': overdue_tasks_count,
    }
    return render(request, 'dashboard.html', context)