from datetime import timedelta
from django import forms
from django.utils import timezone
from containers.models import Container
from customers.models import Customer
from .models import Assignment


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ('customer', 'container', 'expected_return_date', 'deposit_amount')
        labels = {
            'expected_return_date': 'Expected return date',
            'deposit_amount': 'Deposit collected (₹)',
        }
        widgets = {
            'expected_return_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.filter(business=business)
        self.fields['container'].queryset = Container.objects.filter(
            business=business, status=Container.Status.AVAILABLE
        )
        self.fields['expected_return_date'].initial = timezone.localdate() + timedelta(days=7)

    def clean_expected_return_date(self):
        date = self.cleaned_data['expected_return_date']
        if date < timezone.localdate():
            raise forms.ValidationError('The return date cannot be in the past.')
        return date