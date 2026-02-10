from django import forms
from typing import Optional, Dict, Final, List
from .models import Client


class ClientForm(forms.ModelForm):


    class Meta:
        COMMON_CLASSES: Final[str] = (
            'w-full px-4 py-2 border-2 border-blue-600 rounded-lg '
            'focus:ring-2 focus:ring-blue-400 outline-none transition-all'
        )
        model = Client
        fields: List[str] = ['name', 'email', 'phone', 'notes', 'telegram_chat_id']

        widgets: Dict[str, forms.Widget] = {
            'name': forms.TextInput(attrs={'class': COMMON_CLASSES, 'placeholder': 'Имя или Название компании'}),
            'email': forms.EmailInput(attrs={'class': COMMON_CLASSES, 'placeholder': 'example@mail.com'}),
            'phone': forms.TextInput(attrs={'class': COMMON_CLASSES, 'placeholder': '79991234567'}),
            'notes': forms.Textarea(
                attrs={'class': COMMON_CLASSES, 'rows': 3, 'placeholder': 'Дополнительная информация'}),
            'telegram_chat_id': forms.TextInput(attrs={
                'class': f"{COMMON_CLASSES} bg-gray-50",
                'placeholder': 'ID чата (цифрами)'
            }),
        }

    def clean_phone(self) -> Optional[str]:
        """
        Validate and format the phone number field.
        """
        # Explicitly typing the retrieved value
        phone: Optional[str] = self.cleaned_data.get('phone')

        if not phone:
            return phone

        # Extract only digits from the input string
        digits: str = ''.join(filter(str.isdigit, phone))

        # 1. Normalize formatting to start with '7'
        if digits.startswith('8'):
            digits = '7' + digits[1:]
        elif len(digits) == 10:
            digits = '7' + digits

        # 2. Length validation
        if len(digits) != 11:
            raise forms.ValidationError("Номер должен содержать ровно 11 цифр (включая 7)")

        # 3. Leading digit validation
        if not digits.startswith('7'):
            raise forms.ValidationError("Номер должен начинаться с 7 или 8")

        # 4. Database uniqueness check excluding current instance
        if Client.objects.filter(phone=digits).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Этот номер телефона уже используется")

        return digits