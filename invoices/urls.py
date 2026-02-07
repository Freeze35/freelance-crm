from django.urls import path
from .views import invoice_create_from_project, generate_invoice_pdf, invoice_update, invoice_delete,send_invoice_telegram
app_name = 'invoices'

urlpatterns = [
    path('projects/<int:project_id>/invoice/create/', invoice_create_from_project, name='create_from_project'),
    path('<int:invoice_id>/pdf/', generate_invoice_pdf, name='pdf'),
    path('<int:pk>/update/', invoice_update, name='update'),
    path('<int:pk>/delete/', invoice_delete, name='delete'),
    path('<int:pk>/send-telegram/', send_invoice_telegram, name='send_telegram'),
]
