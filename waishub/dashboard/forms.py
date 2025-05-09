from django import forms
from .models import Reminder

class ReminderForm(forms.ModelForm):
    enabled = forms.BooleanField(required=False)
    class Meta:
        model = Reminder
        fields = ['alert_time', 'enabled']  
        widgets = {
            'alert_time': forms.TimeInput(attrs={'type': 'time'}), #Reminder Time
            'enabled': forms.CheckboxInput(attrs={'class': 'checkbox'})  # Notif Enabled
        }
