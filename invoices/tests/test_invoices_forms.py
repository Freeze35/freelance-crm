import pytest
from invoices.forms import InvoiceForm
from django.utils import timezone
from datetime import timedelta

class TestInvoiceForm:

    def test_invoice_form_missing_data(self):
        """Checking if a form is invalid without required fields"""
        form = InvoiceForm(data={})
        assert not form.is_valid()
        assert 'amount' in form.errors
        assert 'due_date' in form.errors

    def test_number_field_not_in_fields(self):
        """Checking that the number field is not processed by the form if it is not in Meta.fields"""
        form_data = {
            'amount': 100,
            'due_date': '2025-01-01',
            'status': 'paid',
            'number': 'INV-999'
        }
        form = InvoiceForm(data=form_data)
        assert form.is_valid()
        # We check that even though we sent a number, it didn't make it into the cleaned data,
        # since it's not in the fields list
        assert 'number' not in form.cleaned_data