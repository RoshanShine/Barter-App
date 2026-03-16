from django import forms
from .models import Product

class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

class ProductForm(forms.ModelForm):
    # Field for multi-image upload
    more_images = forms.FileField(
        widget=MultipleFileInput(attrs={'multiple': True, 'class': 'form-control'}),
        required=False,
        label="Gallery Images"
    )

    class Meta:
        model = Product
        fields = [
            'name',
            'category',
            'image',
            'more_images',
            'description',
            'location',
            'condition',
            'phone',
            'exchange_type',
            'price',
            'barter_description',
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control glass-card text-white border-0 p-3', 'placeholder': 'What are you swapping?'}),
            'category': forms.Select(attrs={'class': 'form-select glass-card text-white border-0 p-3'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control glass-card text-white border-0 p-3'}),
            'description': forms.Textarea(attrs={'class': 'form-control glass-card text-white border-0 p-3', 'rows': 4, 'placeholder': 'Tell us more about it...'}),
            'location': forms.TextInput(attrs={'class': 'form-control glass-card text-white border-0 p-3', 'placeholder': 'e.g., New York, NY'}),
            'condition': forms.TextInput(attrs={'class': 'form-control glass-card text-white border-0 p-3', 'placeholder': 'e.g., Brand New, Mint Condition'}),
            'phone': forms.TextInput(attrs={'class': 'form-control glass-card text-white border-0 p-3', 'placeholder': 'For coordination...'}),
            'exchange_type': forms.Select(attrs={'class': 'form-select glass-card text-white border-0 p-3'}),
            'price': forms.NumberInput(attrs={'class': 'form-control glass-card text-white border-0 p-3', 'placeholder': 'Optional price...'}),
            'barter_description': forms.Textarea(attrs={'class': 'form-control glass-card text-white border-0 p-3', 'rows': 4, 'placeholder': 'What are you looking for in return?'}),
        }