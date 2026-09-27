from django import forms
import re


class TenantCreateForm(forms.Form):
    restaurant_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "e.g. Burger Palace", "class": "form-input"}),
    )
    subdomain = forms.CharField(
        max_length=63,
        help_text="Lowercase letters, numbers, hyphens only. Will be used as: subdomain.localhost",
        widget=forms.TextInput(attrs={"placeholder": "e.g. burger-palace", "class": "form-input"}),
    )
    admin_username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "admin", "class": "form-input"}),
    )
    admin_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"placeholder": "admin@example.com", "class": "form-input"}),
    )
    admin_password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={"placeholder": "Min 6 characters", "class": "form-input"}),
    )
    admin_password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm password", "class": "form-input"}),
    )

    def clean_subdomain(self):
        subdomain = self.cleaned_data["subdomain"].lower().strip()
        if not re.match(r"^[a-z][a-z0-9-]*$", subdomain):
            raise forms.ValidationError("Must start with a letter, only lowercase letters, numbers, hyphens.")
        if subdomain == "public":
            raise forms.ValidationError("'public' is reserved.")
        from tenants.models import Client
        if Client.objects.filter(schema_name=subdomain).exists():
            raise forms.ValidationError("This subdomain is already taken.")
        return subdomain

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get("admin_password")
        pw2 = cleaned.get("admin_password_confirm")
        if pw and pw2 and pw != pw2:
            self.add_error("admin_password_confirm", "Passwords do not match.")
        return cleaned
