from django import forms
from .models import FoodItem

class FoodForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ['name', 'quantity', 'description', 'expiry_date']
        widgets = {
            'expiry_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }