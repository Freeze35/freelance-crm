from django.core.paginator import Paginator, Page
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.db.models import QuerySet
from typing import Union, Optional

from .forms import ClientForm
from .models import Client

# Define a type alias for view responses that render templates
RenderResponse = Union[TemplateResponse, HttpResponse, HttpResponseRedirect]


def client_create(request: HttpRequest) -> RenderResponse:
    """Handle the creation of a new client instance."""
    if request.method == 'POST':
        form: ClientForm = ClientForm(request.POST)
        if form.is_valid():
            client_obj: Client = form.save()
            messages.success(request, f'Client "{client_obj.name}" was successfully added!')

            if request.POST.get('action') == 'save_and_add':
                return redirect('client_create')

            return redirect('dashboard')
    else:
        form = ClientForm()

    return render(request, 'clients/create.html', {'form': form})


def client_list(request: HttpRequest) -> HttpResponse:
    """Display a paginated list of all clients."""
    clients_query: QuerySet[Client] = Client.objects.all().order_by('-created_at')

    # Pagination: 8 clients per page
    paginator: Paginator = Paginator(clients_query, 8)
    page_number: Optional[str] = request.GET.get('page')
    page_obj: Page = paginator.get_page(page_number)

    context: dict = {
        'page_obj': page_obj,
        'clients': page_obj,
    }
    return render(request, 'clients/list.html', context)


def client_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Display detailed information about a specific client."""
    client_obj: Client = get_object_or_404(Client, pk=pk)
    context: dict = {
        'client': client_obj,
    }
    return render(request, 'clients/detail.html', context)


def client_update(request: HttpRequest, pk: int) -> RenderResponse:
    """Update an existing client's information."""
    client_obj: Client = get_object_or_404(Client, pk=pk)

    if request.method == 'POST':
        form: ClientForm = ClientForm(request.POST, instance=client_obj)
        if form.is_valid():
            form.save()
            return redirect('clients:list')
    else:
        form = ClientForm(instance=client_obj)

    return render(request, 'clients/update.html', {'form': form, 'client': client_obj})


@require_POST
def client_delete(request: HttpRequest, pk: int) -> HttpResponseRedirect:
    """Delete a client and redirect to the client list."""
    client_obj: Client = get_object_or_404(Client, pk=pk)
    client_name: str = client_obj.name
    client_obj.delete()

    messages.success(request, f'Client "{client_name}" was successfully deleted.')
    return redirect('clients:list')