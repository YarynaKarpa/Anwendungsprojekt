from django import forms

class TXTUploadForm(forms.Form):
    subject = forms.CharField(
        label="Subject",
        help_text="One subject for all cards in this TXT.",
        required=True,
        max_length=200,
        widget=forms.TextInput(attrs={"placeholder": "e.g. Biology / Math / History"})
    )
    txt = forms.FileField(
        label="TXT file",
        help_text="Upload a .txt with <question> / <answer> pairs",
        required=True,
        widget=forms.ClearableFileInput(attrs={
            "accept": ".txt,text/plain",
            "id": "txt-input"
        })
    )
