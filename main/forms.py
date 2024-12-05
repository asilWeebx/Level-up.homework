from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Level

class CustomUserCreationForm(UserCreationForm):
    level = forms.ModelChoiceField(queryset=Level.objects.all(), empty_label="Choose your level", required=True)

    class Meta:
        model = User
        fields = ['username','first_name','last_name', 'password1', 'password2', 'level']
