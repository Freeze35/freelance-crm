import pytest
from typing import Dict, List, Any
from clients.forms import ClientForm
from clients.models import Client


@pytest.mark.django_db
class TestClientForm:

    def test_form_valid_data(self) -> None:
        """Verify the form accepts valid data and formats the phone number"""

        data: Dict[str, str] = {
            'name': 'Иван Иванов',
            'email': 'ivan@example.com',
            'phone': '89991112233',
            'telegram_chat_id': '12345678'
        }
        form: ClientForm = ClientForm(data=data)

        assert form.is_valid()
        # Ensure '8' at the start is converted to '7'
        assert form.cleaned_data.get('phone') == '79991112233'

    def test_phone_conversion_from_8(self) -> None:
        """Verify that a leading '8' is replaced with '7' during cleaning"""
        form: ClientForm = ClientForm(data={'name': 'Test', 'phone': '89001234567'})
        form.is_valid()
        assert form.cleaned_data.get('phone') == '79001234567'

    def test_phone_too_short(self) -> None:
        """Verify validation error when the phone number is insufficient in length"""
        form: ClientForm = ClientForm(data={'name': 'Test', 'phone': '7900123'})

        assert not form.is_valid()
        assert 'phone' in form.errors

        phone_errors: List[str] = form.errors['phone']
        assert "Номер должен содержать ровно 11 цифр (включая 7)" in phone_errors

    def test_duplicate_phone_validation(self) -> None:
        """Verify uniqueness constraint on the phone number field within the form"""

        Client.objects.create(name="Existing", phone="79990000000")

        form: ClientForm = ClientForm(data={'name': 'New', 'phone': '89990000000'})

        assert not form.is_valid()
        assert "Этот номер телефона уже используется" in form.errors['phone']

    def test_empty_phone_is_allowed(self) -> None:
        """Verify that the phone field is optional in the form"""
        form: ClientForm = ClientForm(data={'name': 'Only Name', 'phone': ''})
        assert form.is_valid()
        assert form.cleaned_data.get('phone') == ''