from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import InvoiceForm
from projects.models import Project
from datetime import timedelta
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.utils import timezone
import base64
import os
from django.conf import settings
import qrcode
from io import BytesIO
from celery import shared_task
from invoices.models import Invoice
from django.test import RequestFactory
from tasks.tasks import send_telegram
from django.views.decorators.http import require_POST
from typing import Union, Optional, Any, Dict

# Type alias for standard view responses
ViewResponse = Union[HttpResponse, Any]


def invoice_create_from_project(request: HttpRequest, project_id: int) -> ViewResponse:
    """Handle invoice creation based on a specific project."""
    project: Project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form: InvoiceForm = InvoiceForm(request.POST)
        if form.is_valid():
            invoice: Invoice = form.save(commit=False)
            invoice.project = project

            # Generate sequential invoice number
            last_invoice: Optional[Invoice] = Invoice.objects.filter(project=project).order_by('-id').first()
            next_num: int = 1 if not last_invoice else int(last_invoice.number.split('-')[-1]) + 1
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


def generate_invoice_pdf(request: HttpRequest, invoice_id: int) -> HttpResponse:
    """Generate and return a PDF document for the given invoice."""
    invoice: Invoice = get_object_or_404(Invoice, pk=invoice_id)

    # Logo processing
    logo_path: str = os.path.join(settings.BASE_DIR, 'static', 'logo.png')
    logo_base64: str = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    # QR Code generation for payment
    qr_data: str = f"ST00012|Name=ИП Иванов И.И.|PersonalAcc=40802810400000001234|BankName=Сбербанк|Sum={int(invoice.amount * 100)}"
    qr_engine: qrcode.QRCode = qrcode.QRCode(version=1, box_size=10, border=5)
    qr_engine.add_data(qr_data)
    qr_engine.make(fit=True)

    qr_img: Any = qr_engine.make_image(fill_color="black", back_color="white")
    qr_buffer: BytesIO = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_code_base64: str = base64.b64encode(qr_buffer.getvalue()).decode('utf-8')

    html_string: str = render_to_string('invoices/pdf_invoice.html', {
        'invoice': invoice,
        'now': timezone.now(),
        'logo_base64': logo_base64,
        'qr_code_base64': qr_code_base64,
    })

    html: HTML = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf_content: bytes = html.write_pdf()

    response: HttpResponse = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.number}.pdf"'
    response.write(pdf_content)
    return response


def invoice_update(request: HttpRequest, pk: int) -> ViewResponse:
    """Update an existing invoice."""
    invoice: Invoice = get_object_or_404(Invoice, pk=pk)
    project: Project = invoice.project

    if request.method == 'POST':
        form: InvoiceForm = InvoiceForm(request.POST, instance=invoice)
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


@require_POST
def invoice_delete(request: HttpRequest, pk: int) -> ViewResponse:
    """Delete an invoice and redirect back to the project detail."""
    invoice: Invoice = get_object_or_404(Invoice, pk=pk)
    project_pk: int = invoice.project.pk
    invoice.delete()
    messages.success(request, f'Счёт {invoice.number} успешно удалён.')
    return redirect('projects:detail', pk=project_pk)


@shared_task
def send_invoice_to_telegram(invoice_id: int, chat_id: Union[int, str]) -> str:
    """Background task to send invoice PDF to Telegram."""
    try:
        invoice: Invoice = Invoice.objects.get(id=invoice_id)

        factory: RequestFactory = RequestFactory()
        fake_request: HttpRequest = factory.get('/')
        pdf_response: HttpResponse = generate_invoice_pdf(fake_request, invoice_id)
        pdf_bytes: bytes = pdf_response.content

        caption: str = (
            f"<b>Счёт №{invoice.number}</b>\n"
            f"Сумма: {invoice.amount} ₽\n"
            f"Проект: {invoice.project.name}\n"
            f"Срок оплаты: {invoice.due_date.strftime('%d.%m.%Y')}\n"
            f"Статус: {invoice.get_status_display()}"
        )

        result: str = send_telegram.run(
            chat_id=chat_id,
            document_bytes=pdf_bytes,
            filename=f"счёт_{invoice.number}.pdf",
            caption=caption
        )
        return result

    except Invoice.DoesNotExist:
        return f"Invoice {invoice_id} not found"
    except Exception as e:
        return f"Error: {str(e)}"


@require_POST
def send_invoice_telegram(request: HttpRequest, pk: int) -> JsonResponse:
    """Trigger the background task to send an invoice via Telegram."""
    invoice: Invoice = get_object_or_404(Invoice, pk=pk)
    client_chat_id: Optional[str] = invoice.project.client.telegram_chat_id

    if client_chat_id:
        chat_id: Union[str, int] = client_chat_id
        recipient: str = "клиенту"
    else:
        chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
        recipient = "администратору"

    if not chat_id:
        return JsonResponse({
            'status': 'error',
            'message': 'ID чата не найден'
        }, status=400)

    send_invoice_to_telegram.delay(invoice.pk, chat_id)

    return JsonResponse({
        'status': 'success',
        'message': f'Счёт успешно отправлен {recipient}'
    })