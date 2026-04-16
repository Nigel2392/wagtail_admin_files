from django import forms
from django.utils.translation import gettext_lazy as _
from django.forms import modelformset_factory
from .models import SharedFile

class SharedFileForm(forms.ModelForm):
    class Meta:
        model = SharedFile
        fields = ['title', 'file', 'group']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': _('Enter file title')}),
            'group': forms.HiddenInput(), # Usually passed via context, not manual entry
        }

# This creates a management object for multiple SharedFile forms
SharedFileFormSet = modelformset_factory(
    SharedFile,
    form=SharedFileForm,
    extra=0,       # Number of empty forms to display
)