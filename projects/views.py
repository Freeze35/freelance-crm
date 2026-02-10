from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator, Page
from django.db.models import Count, Q, QuerySet
from django.utils import timezone
from django.http import HttpRequest, HttpResponse
from typing import Union, Any, Dict, Optional

from .models import Project
from .forms import ProjectForm
from tasks.models import Task

ViewResponse = Union[HttpResponse, Any]

def project_list(request: HttpRequest) -> ViewResponse:
    """Display a list of projects with task statistics annotations."""
    projects: QuerySet[Project] = Project.objects.all().order_by('-created_at').annotate(
        todo_count=Count('tasks', filter=Q(tasks__status='todo')),
        in_progress_count=Count('tasks', filter=Q(tasks__status='in_progress')),
        done_count=Count('tasks', filter=Q(tasks__status='done')),
        canceled_count=Count('tasks', filter=Q(tasks__status='canceled')),
        total_tasks=Count('tasks'),
    )

    paginator: Paginator = Paginator(projects, 8)
    page_number: Optional[str] = request.GET.get('page')
    page_obj: Page = paginator.get_page(page_number)

    context: Dict[str, Any] = {
        'page_obj': page_obj,
        'projects': page_obj,
    }
    return render(request, 'projects/list.html', context)


def project_create(request: HttpRequest) -> ViewResponse:
    """Handle project creation, optionally pre-selecting a client via GET parameter."""
    if request.method == 'POST':
        form: ProjectForm = ProjectForm(request.POST)
        if form.is_valid():
            project: Project = form.save()
            messages.success(request, f'Проект "{project.name}" успешно создан!')
            return redirect('projects:list')
    else:
        client_id: Optional[str] = request.GET.get('client')
        initial_data: Dict[str, Any] = {}
        if client_id:
            initial_data['client'] = client_id

        form = ProjectForm(initial=initial_data)

    return render(request, 'projects/create.html', {'form': form})


def project_detail(request: HttpRequest, pk: int) -> ViewResponse:
    """Display detailed project information, including paginated tasks and invoices."""
    project: Project = get_object_or_404(Project, pk=pk)

    # Tasks pagination
    tasks: QuerySet[Task] = project.tasks.all().order_by('deadline')
    task_paginator: Paginator = Paginator(tasks, 4)
    task_page_number: Optional[str] = request.GET.get('task_page')
    task_page_obj: Page = task_paginator.get_page(task_page_number)

    # Invoices pagination
    invoices: Any = project.invoices.all().order_by('-created_at')
    invoice_paginator: Paginator = Paginator(invoices, 4)
    invoice_page_number: Optional[str] = request.GET.get('invoice_page')
    invoice_page_obj: Page = invoice_paginator.get_page(invoice_page_number)

    context: Dict[str, Any] = {
        'project': project,
        'page_obj': task_page_obj,
        'tasks': task_page_obj,
        'today': timezone.now().date(),
        'invoices': invoice_page_obj,
        'invoice_paginator': invoice_paginator,
    }
    return render(request, 'projects/detail.html', context)


def project_update(request: HttpRequest, pk: int) -> ViewResponse:
    """Update an existing project's details."""
    project: Project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form: ProjectForm = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Проект "{project.name}" успешно обновлён!')
            return redirect('projects:detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'projects/update.html', {'form': form, 'project': project})


def project_delete(request: HttpRequest, pk: int) -> ViewResponse:
    """Handle project deletion with a confirmation requirement."""
    project: Project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project_name: str = project.name
        project.delete()
        messages.success(request, f'Проект "{project_name}" успешно удалён.')
        return redirect('projects:list')
    return render(request, 'projects/delete_confirm.html', {'project': project})


def overdue_tasks(request: HttpRequest) -> ViewResponse:
    """Display a global list of overdue tasks across all projects."""
    today: timezone.datetime.date = timezone.now().date()

    overdue_queryset: QuerySet[Task] = Task.objects.filter(
        deadline__lt=today,
        status__in=['todo', 'in_progress']
    ).select_related('project').order_by('deadline')

    paginator: Paginator = Paginator(overdue_queryset, 12)
    page_number: Optional[str] = request.GET.get('page')
    page_obj: Page = paginator.get_page(page_number)

    context: Dict[str, Any] = {
        'page_obj': page_obj,
        'total_overdue': overdue_queryset.count(),
        'today': today,
    }
    return render(request, 'projects/overdue.html', context)