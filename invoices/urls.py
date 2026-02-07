from django.urls import path
from .views import invoice_create_from_project, generate_invoice_pdf,invoice_update

app_name = 'invoices'

urlpatterns = [
    path('projects/<int:project_id>/invoice/create/', invoice_create_from_project, name='create_from_project'),
    path('<int:invoice_id>/pdf/', generate_invoice_pdf, name='pdf'),
    path('<int:pk>/update/', invoice_update, name='update'),
]
