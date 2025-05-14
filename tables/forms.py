from django import forms
from .models import Business, Table, MenuItem, Category, Review

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


class AddStaffForm(forms.Form):
    email = forms.EmailField(label="Staff Email", widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "Enter staff email"
    }))

    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "Enter password"
    }))

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'photo']
        widgets = {
            'rating': forms.Select(choices=[(i, f"{i} ★") for i in range(1, 6)], attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Leave a comment...'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
