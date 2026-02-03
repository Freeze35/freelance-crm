from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Project
from .forms import ProjectForm
from django.db.models import Count, Q

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
        form = ProjectForm()

    return render(request, 'projects/create.html', {'form': form})

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'projects/detail.html', {'project': project})

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