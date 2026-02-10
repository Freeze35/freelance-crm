# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import InvoiceForm
from projects.models import Project
from datetime import timedelta
from django.http import HttpResponse
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
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.contrib.staticfiles import finders

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

    # ЛОГОТИП: Используем finders, чтобы найти файл и в разработке, и в деплое
    logo_path = finders.find('logo.png')
    logo_base64 = ""

    if logo_path and os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    # QR CODE GENERATOR (твой обновленный код — он теперь верный)
    qr_data = f"ST00012|Name=ИП Иванов И.И.|PersonalAcc=40802810400000001234|BankName=Сбербанк|BIC=044525974|CorrespAcc=30101810145250000974|Sum={int(invoice.amount * 100)}"

    qr_engine = qrcode.QRCode(version=1, box_size=10, border=5)
    qr_engine.add_data(qr_data)
    qr_engine.make(fit=True)
    qr = qr_engine.make_image(fill_color="black", back_color="white")

    qr_buffer = BytesIO()
    qr.save(qr_buffer, format="PNG")
    qr_code_base64 = base64.b64encode(qr_buffer.getvalue()).decode('utf-8')

    html_string = render_to_string('invoices/pdf_invoice.html', {
        'invoice': invoice,
        'now': timezone.now(),
        'logo_base64': logo_base64,
        'qr_code_base64': qr_code_base64,
    })

    # Для PDF важно указать base_url, чтобы WeasyPrint понимал относительные пути
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf = html.write_pdf()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.number}.pdf"'
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

@require_POST
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    project_pk = invoice.project.pk  # запоминаем проект для редиректа
    invoice.delete()
    messages.success(request, f'Счёт {invoice.number} успешно удалён.')
    return redirect('projects:detail', pk=project_pk)

@shared_task
def send_invoice_to_telegram(invoice_id: int, chat_id: int | str):
    try:
        invoice = Invoice.objects.get(id=invoice_id)

        # Generate PDF in memory
        factory = RequestFactory()
        fake_request = factory.get('/')
        pdf_response = generate_invoice_pdf(fake_request, invoice_id)
        pdf_bytes = pdf_response.content

        caption = (
            f"<b>Счёт №{invoice.number}</b>\n"
            f"Сумма: {invoice.amount} ₽\n"
            f"Проект: {invoice.project.name}\n"
            f"Срок оплаты: {invoice.due_date.strftime('%d.%m.%Y')}\n"
            f"Статус: {invoice.get_status_display()}"
        )


        result = send_telegram.run(
            chat_id=chat_id,
            document_bytes=pdf_bytes,
            filename=f"счёт_{invoice.number}.pdf",
            caption=caption
        )

        return result

    except Invoice.DoesNotExist:
        return f"Счёт {invoice_id} не найден"
    except Exception as e:
        return f"Ошибка: {str(e)}"


@require_POST
def send_invoice_telegram(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    client_chat_id = invoice.project.client.telegram_chat_id

    if client_chat_id:
        chat_id = client_chat_id
        recipient = "клиенту"
    else:
        chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
        recipient = "администратору"

    if not chat_id:
        return JsonResponse({
            'status': 'error', # Добавили статус ошибки
            'message': 'ID чата не найден'
        }, status=400)

    # Запускаем задачу
    send_invoice_to_telegram.delay(invoice.pk, chat_id)

    # ВАЖНО: Добавляем 'status': 'success'
    return JsonResponse({
        'status': 'success',
        'message': f'Счёт успешно отправлен {recipient}'
    })