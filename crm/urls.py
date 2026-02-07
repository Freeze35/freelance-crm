from django.contrib import admin
from .views import dashboard
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('projects/', include('projects.urls')),
    path('clients/', include('clients.urls')),
    path('tasks/', include('tasks.urls')),
    path('invoices/', include('invoices.urls')),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico'))),
]
