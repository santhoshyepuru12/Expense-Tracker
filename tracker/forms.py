from django import forms
from .models import Expense,Budget
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["title", "amount", "category", "date", "description"]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Lunch, Electricity Bill, Bus Ticket"
            }),
            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter amount",
                "min": "0",
                "step": "0.01"
            }),
            "category": forms.Select(attrs={
                "class": "form-select"
            }),
            "date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Add additional details about this expense (optional)",
                "rows": 3
            }),
        }


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=100,
        required=True,
        label="Name",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your name"
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your email address"
        })
    )

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Choose a username"
        })
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Create a password"
        })
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your password again"
        })
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "username",
            "email",
            "password1",
            "password2",
        ]


        
class UpdateProfileForm(forms.ModelForm):

    first_name = forms.CharField(
        label="Name",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your name"
        })
    )

    class Meta:
        model = User
        fields = ["first_name"]



class BudgetForm(forms.ModelForm):

    month = forms.DateField(
        input_formats=["%Y-%m"],
        widget=forms.DateInput(
            format="%Y-%m",
            attrs={
                "class": "form-control",
                "type": "month"
            }
        )
    )

    class Meta:
        model = Budget
        fields = ["amount", "month"]

        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter monthly budget"
                }
            ),
        }