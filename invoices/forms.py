from django import forms
from .models import Invoice

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['amount', 'due_date', 'status']
        common_classes = 'w-full px-4 py-2 border-2 border-blue-600 rounded-lg focus:ring-2 focus:ring-blue-400 outline-none transition-all'
        widgets = {
            'number': forms.TextInput(attrs={
                'class': common_classes,
                'placeholder': 'INV-001'
            }),
            'amount': forms.NumberInput(attrs={
                'class': common_classes,
                'placeholder': '0.00'
            }),
            'due_date': forms.DateInput(attrs={
                'class': common_classes,
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': common_classes
            }),
        }