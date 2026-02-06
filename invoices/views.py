# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Invoice
from .forms import InvoiceForm
from projects.models import Project
from datetime import timedelta
from django.utils import timezone

def invoice_create_from_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.project = project
            # Автоматический номер счёта (INV-год-последовательный номер)
            last_invoice = Invoice.objects.filter(project=project).order_by('-id').first()
            next_num = 1 if not last_invoice else int(last_invoice.number.split('-')[-1]) + 1
            invoice.number = f"INV-{timezone.now().year}-{next_num:03d}"
            invoice.save()
            messages.success(request, f'Счёт {invoice.number} успешно создан!')
            return redirect('projects:detail', pk=project.pk)
    else:
        form = InvoiceForm(initial={
            'amount': project.budget or 0,
            'due_date': timezone.now().date() + timedelta(days=14),
        })

    return render(request, 'invoices/create.html', {
        'form': form,
        'project': project
    })