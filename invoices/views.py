# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import InvoiceForm
from projects.models import Project
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from invoices.models import Invoice
from weasyprint import HTML


def invoice_create_from_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.project = project
            # Automatic account number (INV-year-sequential number)
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

def generate_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    # Render the template into a string
    html_string = render_to_string('invoices/pdf_invoice.html', {
        'invoice': invoice,
        'now': timezone.now(),
    })

    # Generate PDF
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    # Send as a downloadable file
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="счёт_{invoice.number}.pdf"'
    response.write(pdf)
    return response


def invoice_update(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    project = invoice.project

    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            messages.success(request, f'Счёт {invoice.number} обновлён!')
            return redirect('projects:detail', pk=project.pk)
    else:
        form = InvoiceForm(instance=invoice)

    return render(request, 'invoices/update.html', {
        'form': form,
        'invoice': invoice,
        'project': project,
    })