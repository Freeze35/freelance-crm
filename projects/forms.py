from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'client', 'description', 'budget', 'status', 'deadline']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'budget': forms.NumberInput(attrs={'step': '0.01'}),
        }