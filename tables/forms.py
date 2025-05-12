from django import forms
from .models import Business, Table, MenuItem, Category

class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['table_number']
        widgets = {
            'table_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1})
        }

class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Please enter the name of the business'})
        }

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['item_name', 'description', 'price', 'image', 'category', 'available']
        labels = {
            'item_name': 'Name of dish',
            'description': 'Descriptions',
            'price': 'Price',
            'image': 'Image of dish',
            'category': 'Category',
            'available': 'Available or not'
        }
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'available': forms.CheckboxInput()
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        labels = {'name': 'Category name'}
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Main course / Drinks / Snacks'})
        }
