from django import forms
from .models import SavingsGoal, Saving

class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ['name', 'target_amount', 'term', 'reminder']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., Emergency Fund'}),
            'target_amount': forms.NumberInput(attrs={'placeholder': 'e.g., 10000'}),
        }
class SavingForm(forms.ModelForm):
    class Meta:
        model = Saving
        fields = ['date', 'amount', 'goal']  # Include goal field