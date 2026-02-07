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

def invoice_create_from_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.project = project

            # Automatic number: INV-year-sequential number (3 digits)
            current_year = timezone.now().year
            # We calculate how many invoices there are already for this year (for the entire project or globally)
            last_invoice = Invoice.objects.filter(
                number__startswith=f"INV-{current_year}"
            ).order_by('-number').first()

            if last_invoice:
                last_num = int(last_invoice.number.split('-')[-1])
                next_num = last_num + 1
            else:
                next_num = 1

            invoice.number = f"INV-{current_year}-{next_num:03d}"  # 001, 002, 003...

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