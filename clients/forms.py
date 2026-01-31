from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'notes']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            return phone

        # Remove everything except numbers
        digits = ''.join(filter(str.isdigit, phone))

        # We convert it to 7XXXXXXXXXX (11 digits)
        if digits.startswith('8'):
            digits = '7' + digits[1:]
        elif digits.startswith('7'):
            pass
        elif len(digits) == 10:
            digits = '7' + digits
        else:
            raise forms.ValidationError("Номер должен содержать 10 цифр после кода страны")

        # Final length check - must be exactly 11 digits
        if len(digits) != 11:
            raise forms.ValidationError("Номер должен содержать ровно 10 цифр после +7")

        formatted = f'+7{digits[1:]}'

        # Checking uniqueness
        if Client.objects.filter(phone=formatted).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Этот номер телефона уже используется")

        return formatted