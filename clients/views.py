from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import ClientForm
from .models import Client

def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, f'Клиент "{client.name}" успешно добавлен!')

            if request.POST.get('action') == 'save_and_add':
                return redirect('client_create')

            return redirect('dashboard')

    else:
        form = ClientForm()

    return render(request, 'clients/create.html', {'form': form})

def client_list(request):

    clients = Client.objects.all().order_by('-created_at')

    # Pagination: 8 clients per page
    paginator = Paginator(clients, 8)  # 8 элементов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'clients': page_obj,
    }
    return render(request, 'clients/list.html', context)

def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    context = {
        'client': client,
    }
    return render(request, 'clients/detail.html', context)

def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('clients:list')  # or 'client_detail' or 'dashboard'
    else:
        form = ClientForm(instance=client)
    return render(request, 'clients/update.html', {'form': form, 'client': client})

@require_POST
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client_name = client.name  # сохраняем имя для сообщения
    client.delete()
    messages.success(request, f'Клиент "{client_name}" успешно удалён.')
    return redirect('clients:list')