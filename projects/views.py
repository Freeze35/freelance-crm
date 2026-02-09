from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Project
from .forms import ProjectForm
from django.db.models import Count, Q
from django.utils import timezone
from tasks.models import Task
from django.shortcuts import get_object_or_404

def project_list(request):
    projects = Project.objects.all().order_by('-created_at').annotate(
        todo_count=Count('tasks', filter=Q(tasks__status='todo')),
        in_progress_count=Count('tasks', filter=Q(tasks__status='in_progress')),
        done_count=Count('tasks', filter=Q(tasks__status='done')),
        canceled_count=Count('tasks', filter=Q(tasks__status='canceled')),
        total_tasks=Count('tasks'),
    )

    paginator = Paginator(projects, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'projects': page_obj,
    }
    return render(request, 'projects/list.html', context)


def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Проект "{project.name}" успешно создан!')
            return redirect('projects:list')
    else:
        # 1. Get the client ID from the GET parameter (for example, ?client=5)
        client_id = request.GET.get('client')

        # 2. Pass this ID to the 'initial' form data
        initial_data = {}
        if client_id:
            initial_data['client'] = client_id

        form = ProjectForm(initial=initial_data)

    return render(request, 'projects/create.html', {'form': form})


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)

    tasks = project.tasks.all().order_by('deadline')
    task_paginator = Paginator(tasks, 4)
    task_page_number = request.GET.get('task_page')
    task_page_obj = task_paginator.get_page(task_page_number)

    # Accounts - New Pagination
    invoices = project.invoices.all().order_by('-created_at')
    invoice_paginator = Paginator(invoices, 4)
    invoice_page_number = request.GET.get('invoice_page')
    invoice_page_obj = invoice_paginator.get_page(invoice_page_number)

    context = {
        'project': project,
        'page_obj': task_page_obj,
        'tasks': task_page_obj,
        'today': timezone.now().date(),
        'invoices': invoice_page_obj,
        'invoice_paginator': invoice_paginator,
    }
    return render(request, 'projects/detail.html', context)


def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Проект "{project.name}" успешно обновлён!')
            return redirect('projects:detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'projects/update.html', {'form': form, 'project': project})


def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'Проект "{project_name}" успешно удалён.')
        return redirect('projects:list')
    return render(request, 'projects/delete_confirm.html', {'project': project})


def overdue_tasks(request):
    today = timezone.now().date()

    overdue = Task.objects.filter(
        deadline__lt=today,
        status__in=['todo', 'in_progress']
    ).select_related('project').order_by('deadline')

    paginator = Paginator(overdue, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total_overdue': overdue.count(),
        'today': today,
    }
    return render(request, 'projects/overdue.html', context)