from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ("user",)

    def __init__(self, *args, **kwargs):
        """Initialise the form."""
        super().__init__(*args, **kwargs)
        placeholders = self._placeholders()
        self.fields["default_phone_number"].widget.attrs["autofocus"] = True
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = (
                "border-black rounded-0 profile-form-input"
            )
            field.label = False
            placeholder = placeholders.get(field_name)
            if placeholder:
                if field.required:
                    placeholder += " *"
                field.widget.attrs["placeholder"] = placeholder

    def _placeholders(self):
        """Return form field placeholders."""
        return {
            "default_phone_number": "Phone Number",
            "default_postcode": "Postal Code",
            "default_town_or_city": "Town or City",
            "default_street_address1": "Street Address 1",
            "default_street_address2": "Street Address 2",
            "default_county": "County, State or Locality",
        }
