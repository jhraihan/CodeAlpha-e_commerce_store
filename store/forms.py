from django import forms

from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["full_name", "email", "phone", "address", "city", "postal_code"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "full_name": "Full name",
            "postal_code": "Postal code",
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = [c for c in phone if c.isdigit()]
        if len(digits) < 7:
            raise forms.ValidationError("Enter a phone number we can reach you on.")
        return phone
