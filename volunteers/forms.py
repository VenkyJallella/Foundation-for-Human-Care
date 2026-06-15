from django import forms

from .models import Application


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ("message",)
        widgets = {
            "message": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Tell us why you'd like to volunteer..."}
            )
        }
