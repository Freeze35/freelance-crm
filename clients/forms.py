from django import forms
from .models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client

        fields = ['name', 'email', 'phone', 'notes', 'telegram_chat_id']

        common_classes = 'w-full px-4 py-2 border-2 border-blue-600 rounded-lg focus:ring-2 focus:ring-blue-400 outline-none transition-all'

        widgets = {
            'name': forms.TextInput(attrs={'class': common_classes, 'placeholder': 'Имя или Название компании'}),
            'email': forms.EmailInput(attrs={'class': common_classes, 'placeholder': 'example@mail.com'}),
            'phone': forms.TextInput(attrs={'class': common_classes, 'placeholder': '79991234567'}),
            'notes': forms.Textarea(
                attrs={'class': common_classes, 'rows': 3, 'placeholder': 'Дополнительная информация'}),
            'telegram_chat_id': forms.TextInput(attrs={
                'class': common_classes + ' bg-gray-50',  # Выделим цветом, так как оно часто автозаполняется
                'placeholder': 'ID чата (цифрами)'
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            return phone

        # We leave only numbers
        digits = ''.join(filter(str.isdigit, phone))

        # 1. Converting to format 7...
        if digits.startswith('8'):
            digits = '7' + digits[1:]
        elif len(digits) == 10:
            digits = '7' + digits

        # 2. Checking the length
        if len(digits) != 11:
            raise forms.ValidationError("Номер должен содержать ровно 11 цифр (включая 7)")

        #3. Check the format (must start with 7)
        if not digits.startswith('7'):
            raise forms.ValidationError("Номер должен начинаться с 7 или 8")

        # 4. Checking uniqueness
        if Client.objects.filter(phone=digits).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Этот номер телефона уже используется")

        return digits