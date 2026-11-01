from django import forms
from django.db import transaction
from .models import Business, User


class QuickRegisterForm(forms.Form):
    business_name = forms.CharField(max_length=150, label='Business name')
    business_type = forms.ChoiceField(choices=Business.BUSINESS_TYPES)
    name = forms.CharField(max_length=100, label='Your name')
    phone = forms.CharField(max_length=15, label='Mobile number (used to login)')
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if User.objects.filter(username=phone).exists():
            raise forms.ValidationError('This mobile number is already registered.')
        return phone

    @transaction.atomic
    def save(self):
        data = self.cleaned_data
        business = Business.objects.create(
            name=data['business_name'],
            business_type=data['business_type'],
            phone=data['phone'],
        )
        return User.objects.create_user(
            username=data['phone'],
            password=data['password'],
            first_name=data['name'],
            phone=data['phone'],
            business=business,
            role=User.Role.ADMIN,
        )


class StaffForm(forms.Form):
    name = forms.CharField(max_length=100, label='Staff name')
    phone = forms.CharField(max_length=15, label='Mobile number (used to login)')
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        if User.objects.filter(username=phone).exists():
            raise forms.ValidationError('This mobile number is already registered.')
        return phone

    def save(self, business):
        data = self.cleaned_data
        return User.objects.create_user(
            username=data['phone'],
            password=data['password'],
            first_name=data['name'],
            phone=data['phone'],
            business=business,
            role=User.Role.STAFF,
        )