from django import forms
from .models import Client
class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'notes']
        common_classes = 'w-full px-4 py-2 border-2 border-blue-600 rounded-lg focus:ring-2 focus:ring-blue-400 outline-none transition-all'
        widgets = {
            'name': forms.TextInput(attrs={'class': common_classes, 'placeholder': 'Название проекта'}),
            'client': forms.Select(attrs={'class': common_classes}),
            'description': forms.Textarea(attrs={'class': common_classes, 'rows': 3}),
            'budget': forms.NumberInput(attrs={'class': common_classes}),
            'status': forms.Select(attrs={'class': common_classes}),
            'deadline': forms.DateInput(attrs={'class': common_classes, 'type': 'date'}),
        }

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

        if len(digits) != 11:
            raise forms.ValidationError("Номер должен содержать ровно 10 цифр после +7")

        # Uniqueness check (by numbers, without the "+" sign)
        if Client.objects.filter(phone=digits).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Этот номер телефона уже используется")

        return digits