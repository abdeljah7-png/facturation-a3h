from django import forms
from .models import (
    MessageSpec,
    ReportingEntity,
    CbcBody,
    CbcReport,
    Summary
)


class MessageSpecForm(forms.ModelForm):

    class Meta:
        model = MessageSpec
        fields = "__all__"


class ReportingEntityForm(forms.ModelForm):

    class Meta:
        model = ReportingEntity
        fields = "__all__"


class CbcBodyForm(forms.ModelForm):

    class Meta:
        model = CbcBody
        fields = "__all__"


class CbcReportForm(forms.ModelForm):

    class Meta:
        model = CbcReport
        fields = "__all__"


class SummaryForm(forms.ModelForm):

    class Meta:
        model = Summary
        fields = "__all__"