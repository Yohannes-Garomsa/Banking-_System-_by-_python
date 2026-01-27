from django import forms
from .models import Account

class AccountForm(forms.ModelForm):
    class Meta:
        model=Account
        fields =['owner', 'balance']
        # Adding Bootstrap styling to the form fields
        widgets ={
            'owner':forms.TextInput(attrs={'class':'form-control','placeholder':'Full Name'}),
            'balance':forms.NumberInput(attrs={'class':'form-control', 'placeholder': 'Initial Deposit'})
        }
        