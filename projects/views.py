from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Project
from .forms import ProjectForm
from django.core.paginator import Paginator

def project_list(request):

    projects = Project.objects.all().order_by('-created_at')

    # Pagination: 8
    paginator = Paginator(projects, 8)  # 8 элементов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'clients': page_obj,
    }
    return render(request, 'projects/list.html', context)

def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Проект "{project.name}" успешно создан!')
            return redirect('project_list')
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
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/update.html', {'form': form, 'project': project})

def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'Проект "{project_name}" успешно удалён.')
        return redirect('project_list')
    return render(request, 'projects/delete.html', {'project': project})