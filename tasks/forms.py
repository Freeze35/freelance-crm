from django import forms
from .models import Task
from typing import Dict, Any

# forms.py
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields: list[str] = ['title', 'description', 'status', 'deadline']

        # Tailwind CSS classes for consistent styling
        common_classes: str = (
            'w-full px-4 py-2 border-2 border-blue-600 rounded-lg '
            'focus:ring-2 focus:ring-blue-400 outline-none transition-all'
        )

        widgets: Dict[str, Any] = {
            'title': forms.TextInput(attrs={
                'class': common_classes,
                'placeholder': 'Название задачи...'
            }),
            'description': forms.Textarea(attrs={
                'class': common_classes,
                'rows': 3,
                'placeholder': 'Что нужно сделать?'
            }),
            'status': forms.Select(attrs={
                'class': common_classes
            }),
            'deadline': forms.DateInput(attrs={
                'class': common_classes,
                'type': 'date'
            }),
        }