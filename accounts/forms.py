from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        label='Ism',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ismingiz'}),
    )
    last_name = forms.CharField(
        max_length=50,
        label='Familiya',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Familiyangiz'}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
    )
    grade = forms.ChoiceField(
        choices=[('', 'Sinfni tanlang')] + [(i, f'{i}-sinf') for i in range(1, 12)],
        label='Sinf',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    language = forms.ChoiceField(
        choices=User.LANGUAGE_CHOICES,
        label='Til',
        initial='uz',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    password1 = forms.CharField(
        label='Parol',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
    )
    password2 = forms.CharField(
        label='Parolni tasdiqlang',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'grade', 'language', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu email allaqachon ro'yxatdan o'tgan.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com',
            'autofocus': True,
        }),
    )
    password = forms.CharField(
        label='Parol',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
    )


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'grade', 'language', 'avatar', 'bio')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'grade': forms.Select(attrs={'class': 'form-select'}),
            'language': forms.Select(attrs={'class': 'form-select'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'first_name': 'Ism',
            'last_name': 'Familiya',
            'grade': 'Sinf',
            'language': 'Til',
            'avatar': 'Avatar',
            'bio': "Qisqacha ma'lumot",
        }
