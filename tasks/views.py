from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Task
from .forms import TaskForm
from projects.models import Project
from django.views.decorators.http import require_POST

def task_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
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

def task_update(request, pk):  # ← меняем task_id → pk
    task = get_object_or_404(Task, pk=pk)
    project = task.project

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
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

def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'tasks/detail.html', {'task': task})

@require_POST
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    project_pk = task.project.pk
    task_title = task.title
    task.delete()
    messages.success(request, f'Задача "{task_title}" успешно удалена.')
    return redirect('projects:detail', pk=project_pk)
