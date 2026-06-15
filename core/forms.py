from django import forms

from .models import ContactMessage, NewsletterSubscriber


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "subject", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ("email",)
        widgets = {
            "email": forms.EmailInput(
                attrs={"placeholder": "Enter your email", "class": "form-control"}
            )
        }

    def clean_email(self):
        email = self.cleaned_data["email"]
        if NewsletterSubscriber.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("You are already subscribed.")
        return email
