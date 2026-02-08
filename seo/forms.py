from django import forms


class URLForm(forms.Form):
    url = forms.URLField(
        max_length=2000,
        widget=forms.URLInput(attrs={
            "placeholder": "https://example.com",
            "class": "form-input",
        }),
    )


class KeywordForm(forms.Form):
    seed_keyword = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            "placeholder": "e.g. best running shoes",
            "class": "form-input",
        }),
    )


class ChatForm(forms.Form):
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            "rows": 3,
            "placeholder": "Ask an SEO question...",
            "class": "form-input",
        }),
    )
