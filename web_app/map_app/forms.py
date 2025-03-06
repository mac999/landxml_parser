from django import forms
from .models import upload_file_model

class FilesForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
			
	upload_file = forms.FileField(widget = forms.TextInput(attrs={
			"type": "File",
			"class": "form-control",
			"multiple": "True",
		}), label = "")

	class Meta:
		model = upload_file_model
		fields = []
