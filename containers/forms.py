from django import forms
from .models import Container


class ContainerForm(forms.ModelForm):
    class Meta:
        model = Container
        fields = ('code', 'container_type', 'capacity', 'notes')
        labels = {
            'code': 'Container ID (e.g. WTR-001)',
            'container_type': 'Type (e.g. Water Can)',
            'capacity': 'Capacity (e.g. 20 L)',
        }
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = business

    def clean_code(self):
        code = self.cleaned_data['code'].strip().upper()
        if Container.objects.filter(business=self.business, code=code).exists():
            raise forms.ValidationError('You already have a container with this ID.')
        return code