from django import forms
from .models import Event


class EventForms(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'time', 'location']
