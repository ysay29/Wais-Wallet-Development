from django import forms
from .models import SavingsGoal

class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ['name', 'target_amount', 'term', 'reminder']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., Emergency Fund'}),
            'target_amount': forms.NumberInput(attrs={'placeholder': 'e.g., 10000'}),
        }
