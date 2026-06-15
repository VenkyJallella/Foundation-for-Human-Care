from django import forms

from .models import Album


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """A file field that accepts several files selected at once."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_clean(d, initial) for d in data]
        if data:
            return [single_clean(data, initial)]
        return []


class AlbumAdminForm(forms.ModelForm):
    bulk_photos = MultipleFileField(
        required=False,
        label="Upload photos",
        help_text="Select several images at once (Ctrl/Cmd-click) to add them all to this album.",
    )

    class Meta:
        model = Album
        fields = "__all__"
