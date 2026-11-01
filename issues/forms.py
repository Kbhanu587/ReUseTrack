from django import forms
from .models import Issue


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ('kind', 'description')
        labels = {
            'kind': 'What happened?',
            'description': 'Describe the issue',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }