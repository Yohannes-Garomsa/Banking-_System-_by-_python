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

class TransferForm(forms.Form):
    # we use modelchoiceField to show a dropdown of existing users
    sender=forms.ModelChoiceField(queryset=Account.objects.all(), empty_label="select Sender")
    receiver=forms.ModelChoiceField(queryset=Account.objects.all(), empty_label="select Receiver")
    amount=forms.DecimalField(min_value=0.01, max_digits=10, decimal_places=2)
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
       # This loop automatically adds 'form-control' to every field in the form
        for field in self.fields.values():
            field.widget.attrs.update({'class':'form-control'})