from django.shortcuts import render
from django.utils import timezone
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.db.models import QuerySet
from typing import Union, Any, Dict

from clients.models import Client
from projects.models import Project
from tasks.models import Task

# Type alias for the view response
ViewResponse = Union[HttpResponse, TemplateResponse]


def dashboard(request: HttpRequest) -> ViewResponse:
    """
    Main dashboard view calculating project and task statistics.
    """
    client_count: int = Client.objects.count()

    # Define active projects by excluding 'canceled' status
    active_projects: QuerySet[Project] = Project.objects.exclude(status='canceled')

    # Project statistics
    project_total: int = active_projects.count()
    project_new: int = active_projects.filter(status='new').count()
    project_in_progress: int = active_projects.filter(status='in_progress').count()
    project_done: int = active_projects.filter(status='completed').count()

    # Task statistics: filter for incomplete tasks with past deadlines
    overdue_tasks_count: int = Task.objects.filter(
        status__in=['todo', 'in_progress'],
        deadline__lt=timezone.now().date()
    ).count()

    # Construct context dictionary with explicit typing
    context: Dict[str, Any] = {
        'client_count': client_count,
        'project_total': project_total,
        'project_new': project_new,
        'project_in_progress': project_in_progress,
        'project_done': project_done,
        'overdue_tasks': overdue_tasks_count,
    }

    return render(request, 'dashboard.html', context)