import pytest
from typing import Dict, Any, List
from invoices.forms import InvoiceForm
from django.utils import timezone
from datetime import timedelta


class TestInvoiceForm:
    """Tests for validating the Invoice form logic and field filtering"""

    def test_invoice_form_missing_data(self) -> None:
        """Verify that the form is invalid when required fields are missing"""
        form: InvoiceForm = InvoiceForm(data={})

        assert not form.is_valid()
        # Ensure validation errors exist for required fields
        assert 'amount' in form.errors
        assert 'due_date' in form.errors

    def test_number_field_not_in_fields(self) -> None:
        """Verify that fields not listed in Meta.fields are ignored by the form"""
        # Define form input including a 'number' field that should be excluded
        form_data: Dict[str, Any] = {
            'amount': 100,
            'due_date': '2026-01-01',
            'status': 'paid',
            'number': 'INV-999'
        }
        form: InvoiceForm = InvoiceForm(data=form_data)

        assert form.is_valid()

        # Ensure the 'number' field was not processed into cleaned_data
        # because it is absent from the Meta.fields list
        assert 'number' not in form.cleaned_data