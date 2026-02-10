from django import forms
from .models import Project
from typing import Dict, Any


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields: list[str] = ['name', 'client', 'description', 'budget', 'status', 'deadline']

        # Define Tailwind CSS classes for consistent styling
        common_classes: str = (
            'w-full px-4 py-2 border-2 border-blue-600 rounded-lg '
            'focus:ring-2 focus:ring-blue-400 outline-none transition-all'
        )

        widgets: Dict[str, Any] = {
            'name': forms.TextInput(attrs={'class': common_classes, 'placeholder': 'Название проекта'}),
            'client': forms.Select(attrs={'class': common_classes}),
            'description': forms.Textarea(attrs={'class': common_classes, 'rows': 3}),
            'budget': forms.NumberInput(attrs={'class': common_classes}),
            'status': forms.Select(attrs={'class': common_classes}),
            'deadline': forms.DateInput(attrs={'class': common_classes, 'type': 'date'}),
        }