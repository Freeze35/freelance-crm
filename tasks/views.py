from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from .models import Task
from .forms import TaskForm
from projects.models import Project
from django.views.decorators.http import require_POST
from typing import Union, Any

# Type alias for standard view responses
ViewResponse = Union[HttpResponse, Any]

def task_create(request: HttpRequest, project_id: int) -> ViewResponse:
    """Handle the creation of a new task associated with a specific project."""
    project: Project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form: TaskForm = TaskForm(request.POST)
        if form.is_valid():
            task: Task = form.save(commit=False)
            task.project = project
            task.save()
            messages.success(request, f'Задача "{task.title}" добавлена к проекту "{project.name}"!')
            return redirect('projects:detail', pk=project.pk)
    else:
        form = TaskForm()

    return render(request, 'tasks/create.html', {
        'form': form,
        'project': project
    })

def task_update(request: HttpRequest, pk: int) -> ViewResponse:
    """Update an existing task and redirect back to the project detail view."""
    task: Task = get_object_or_404(Task, pk=pk)
    project: Project = task.project

    if request.method == 'POST':
        form: TaskForm = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f'Задача "{task.title}" обновлена!')
            return redirect('projects:detail', pk=project.pk)
    else:
        form = TaskForm(instance=task)

    return render(request, 'tasks/update.html', {
        'form': form,
        'task': task,
        'project': project
    })

def task_detail(request: HttpRequest, pk: int) -> ViewResponse:
    """Display the details of a specific task."""
    task: Task = get_object_or_404(Task, pk=pk)
    return render(request, 'tasks/detail.html', {'task': task})

@require_POST
def task_delete(request: HttpRequest, pk: int) -> ViewResponse:
    """Delete a task via POST request and redirect to the parent project."""
    task: Task = get_object_or_404(Task, pk=pk)
    project_pk: int = task.project.pk
    task_title: str = task.title
    task.delete()
    messages.success(request, f'Задача "{task_title}" успешно удалена.')
    return redirect('projects:detail', pk=project_pk)