from django import forms
from .models import UploadedImage

class UploadedForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image']

class NumberInputForm(forms.Form):
    number1 = forms.IntegerField(label='Width', required=False)
    number2 = forms.IntegerField(label='Height', required=False)

class nameForm(forms.Form):
    nameGiven = forms.CharField(max_length=200, label='Group name')
