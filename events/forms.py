from django import forms
from .models import Attendee, Event
from django.contrib.auth.models import User

class AttendeeRegistrationForm(forms.ModelForm):
    create_account = forms.BooleanField(
        required=False, 
        initial=False,
        help_text="Create a user account to manage your registrations"
    )
    username = forms.CharField(required=False)
    password = forms.CharField(
        widget=forms.PasswordInput, 
        required=False,
        help_text="Required if creating an account"
    )
    
    class Meta:
        model = Attendee
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'company', 'job_title', 'category', 'dietary_restrictions',
            'create_account', 'username', 'password'
        ]
        widgets = {
            'dietary_restrictions': forms.Textarea(attrs={'rows': 3}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your company name'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your job title'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'dietary_restrictions': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Any dietary restrictions?', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        create_account = cleaned_data.get('create_account')
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        email = cleaned_data.get('email')
        
        # Check if email is already registered for this event
        if self.event and email:
            if Attendee.objects.filter(event=self.event, email=email).exists():
                raise forms.ValidationError("This email is already registered for this event.")
        
        if create_account:
            if not username:
                raise forms.ValidationError("Username is required when creating an account.")
            if not password:
                raise forms.ValidationError("Password is required when creating an account.")
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("Username already exists.")
        
        return cleaned_data

class AttendeeSearchForm(forms.Form):
    search = forms.CharField(required=False, label='Search attendees', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Search by name, email, or company...'
    }))
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + Attendee.EVENT_CATEGORIES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class CheckInForm(forms.Form):
    confirmation_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter confirmation code',
            'autofocus': True
        })
    )
   