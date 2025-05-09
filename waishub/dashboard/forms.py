from django import forms
from .models import Reminder

class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ['alert_time']
        widgets = {
            'alert_time': forms.TimeInput(attrs={'type': 'time'})  # Correctly renders a time picker
        }
