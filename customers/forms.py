from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('name', 'phone', 'address')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = business

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        if Customer.objects.filter(business=self.business, phone=phone).exists():
            raise forms.ValidationError('You already have a customer with this mobile number.')
        return phone


class PortalLoginForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput, min_length=6, label='Set a password for the customer'
    )