from django import forms

from .models import Donation


class DonationForm(forms.ModelForm):
    PRESET_AMOUNTS = [500, 1000, 2500, 5000]

    amount = forms.IntegerField(min_value=10, label="Amount (₹)")

    class Meta:
        model = Donation
        fields = ("name", "email", "phone", "amount", "program", "is_recurring", "message")
        widgets = {
            "message": forms.TextInput(attrs={"placeholder": "Optional message"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["program"].required = False
        self.fields["program"].empty_label = "General fund (where needed most)"
        # Only published programs are selectable.
        from programs.models import Program

        self.fields["program"].queryset = Program.objects.filter(is_published=True)
