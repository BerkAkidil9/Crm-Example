from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class AgentModelForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('email', 'username', 'first_name', 'last_name')

	def __init__(self, *args, **kwargs):
		self.user_instance = kwargs.get('instance')
		super().__init__(*args, **kwargs)

	def clean_email(self):
		email = self.cleaned_data.get('email')
		if self.user_instance:
			if User.objects.filter(email=email).exclude(pk=self.user_instance.pk).exists():
				raise forms.ValidationError("A user with this email already exists.")
		else:
			if User.objects.filter(email=email).exists():
				raise forms.ValidationError("A user with this email already exists.")
		return email

	def clean_username(self):
		username = self.cleaned_data.get('username')
		if self.user_instance:
			if User.objects.filter(username=username).exclude(pk=self.user_instance.pk).exists():
				raise forms.ValidationError("A user with this username already exists.")
		else:
			if User.objects.filter(username=username).exists():
				raise forms.ValidationError("A user with this username already exists.")
		return username