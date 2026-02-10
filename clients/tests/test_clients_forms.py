import pytest
from clients.forms import ClientForm
from clients.models import Client


@pytest.mark.django_db
class TestClientForm:

    def test_form_valid_data(self):
        """Checking the form for correct data"""
        form = ClientForm(data={
            'name': 'Иван Иванов',
            'email': 'ivan@example.com',
            'phone': '89991112233',  # Должно преобразоваться в 79991112233
            'telegram_chat_id': '12345678'
        })
        assert form.is_valid()
        assert form.cleaned_data['phone'] == '79991112233'

    def test_phone_conversion_from_8(self):
        """Checking the replacement of the initial 8 with 7"""
        form = ClientForm(data={'name': 'Test', 'phone': '89001234567'})
        form.is_valid()
        assert form.cleaned_data['phone'] == '79001234567'

    def test_phone_too_short(self):
        """Error checking if the number is too short"""
        form = ClientForm(data={'name': 'Test', 'phone': '7900123'})
        assert not form.is_valid()
        assert 'phone' in form.errors
        assert "Номер должен содержать ровно 11 цифр (включая 7)" in form.errors['phone']

    def test_duplicate_phone_validation(self):
        "Checking the uniqueness of a phone number in a form"""
        # Create a client in the database
        Client.objects.create(name="Existing", phone="79990000000")

        # We are trying to create the same through the form
        form = ClientForm(data={'name': 'New', 'phone': '89990000000'})

        assert not form.is_valid()
        assert "Этот номер телефона уже используется" in form.errors['phone']

    def test_empty_phone_is_allowed(self):
        """Checking if the phone can be empty (blank=True in the model)"""
        form = ClientForm(data={'name': 'Only Name', 'phone': ''})
        assert form.is_valid()
        assert form.cleaned_data['phone'] == ''