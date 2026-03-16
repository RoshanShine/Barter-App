from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'image',
            'location',
            'condition',
            'phone',
            'category',
            'exchange_type',
            'price',
            'barter_description',
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter product description'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
            'condition': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Example: Used for 2 months'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter contact number'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'exchange_type': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price if applicable'}),
            'barter_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'What do you want in exchange?'}),
        }