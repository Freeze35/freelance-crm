from django import forms
from .models import Invoice

class InvoiceForm(forms.ModelForm):
    # Выносим стили в константу
    CSS_CLASS = 'w-full px-4 py-2 border-2 border-blue-600 rounded-lg focus:ring-2 focus:ring-blue-400 outline-none transition-all'

    amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': CSS_CLASS, 'placeholder': '0.00'})
    )
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': CSS_CLASS, 'type': 'date'})
    )
    status = forms.ChoiceField(
        choices=Invoice._meta.get_field('status').choices,
        widget=forms.Select(attrs={'class': CSS_CLASS})
    )

    class Meta:
        model = Invoice
        fields = ['amount', 'due_date', 'status']