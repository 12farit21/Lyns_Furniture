from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    """
    Form for creating orders
    """

    class Meta:
        model = Order
        fields = [
            'full_name',
            'email',
            'phone',
            'contact_method',
            'region',
            'city',
            'street',
            'house',
            'building',
            'apartment'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ФИО'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@mail.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (___) ___-__-__'
            }),
            'contact_method': forms.Select(attrs={
                'class': 'form-control'
            }),
            'region': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Область'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Город'
            }),
            'street': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Улица'
            }),
            'house': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Дом'
            }),
            'building': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Корпус (необязательно)'
            }),
            'apartment': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Квартира (необязательно)'
            }),
        }
