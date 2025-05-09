from django import forms
from .models import Reminder

class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ['alert_time', 'enabled']  # include 'enabled'
        widgets = {
            'alert_time': forms.TimeInput(attrs={'type': 'time'}), #Reminder Time
            'enabled': forms.CheckboxInput(attrs={'class': 'checkbox'})  # Notif Enabled
        }
