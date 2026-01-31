from django.shortcuts import render, redirect
from .forms import ClientForm
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Client

def client_create(request):
    if request.method == 'POST':
        # Phone and email validation
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard') # или куда нужно
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
            return redirect('client_list')  # or 'client_detail' or 'dashboard'
    else:
        form = ClientForm(instance=client)
    return render(request, 'clients/update.html', {'form': form, 'client': client})