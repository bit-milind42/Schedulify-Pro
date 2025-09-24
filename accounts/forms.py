from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, help_text="Your first name")
    last_name = forms.CharField(max_length=150, required=True, help_text="Your last name") 
    email = forms.EmailField(required=True, help_text="A valid email address")
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)
    specialty = forms.CharField(max_length=100, required=False, help_text="Required for providers", label="Specialty")

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'role', 'specialty', 'password1', 'password2')
        exclude = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes and attributes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            
        # Add specific attributes for different field types
        self.fields['role'].widget.attrs.update({'class': 'form-select'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter a strong password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm your password'})
