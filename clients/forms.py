from django import forms
from .models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        # 1. Добавляем поле в список
        fields = ['name', 'email', 'phone', 'notes', 'telegram_chat_id']

        common_classes = 'w-full px-4 py-2 border-2 border-blue-600 rounded-lg focus:ring-2 focus:ring-blue-400 outline-none transition-all'

        # 2. Настраиваем виджеты именно для модели КЛИЕНТА
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

        digits = ''.join(filter(str.isdigit, phone))

        if digits.startswith('8'):
            digits = '7' + digits[1:]
        elif digits.startswith('7'):
            pass
        elif len(digits) == 10:
            digits = '7' + digits
        else:
            raise forms.ValidationError("Номер должен содержать 10 цифр после кода страны")

        if len(digits) != 11:
            raise forms.ValidationError("Номер должен содержать ровно 11 цифр (включая 7)")

        if Client.objects.filter(phone=digits).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Этот номер телефона уже используется")

        return digits