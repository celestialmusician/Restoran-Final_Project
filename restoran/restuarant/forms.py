from django import forms
from .models import MenuItem

class MenuItemForm(forms.ModelForm):

    class Meta:
        model = MenuItem
        exclude = ['uuid', 'is_available']

        widgets = {

            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Item Name'
            }),

            'category': forms.Select(attrs={
                'class': 'form-select'
            }),

            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Price'
            }),

            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter Item Description'
            }),
        }
