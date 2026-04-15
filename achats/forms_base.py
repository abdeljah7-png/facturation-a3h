from django import forms
from core.forms_base import ERPFormMixin
from .models import BonReception

class BonReceptionForm(ERPFormMixin, forms.ModelForm):

    class Meta:
        model = BonAchat
        fields = '__all__'