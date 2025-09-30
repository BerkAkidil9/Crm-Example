from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from leads.models import UserProfile
from phonenumber_field.formfields import PhoneNumberField
from leads.forms import PhoneNumberWidget

User = get_user_model()

class AgentModelForm(forms.ModelForm):
	email = forms.EmailField(
		required=True,
		widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
		help_text='Email address is required'
	)
	phone_number = PhoneNumberField(
		required=True,
		widget=PhoneNumberWidget(),
		help_text="Select your country and enter your phone number (required)"
	)
	password1 = forms.CharField(
		label='New Password',
		widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'}),
		required=False,
		help_text='Leave blank to keep current password.<br><strong>If changing password:</strong><ul><li>At least 8 characters</li><li>Cannot be entirely numeric</li><li>Cannot be too common (like "password123")</li><li>Cannot be too similar to your username or email</li></ul>'
	)
	password2 = forms.CharField(
		label='Confirm New Password',
		widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}),
		required=False,
		help_text='Enter the same password as above, for verification'
	)

	class Meta:
		model = User
		fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender')
		widgets = {
			'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
			'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
			'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
			'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
		}

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
	
	def clean_phone_number(self):
		phone_number = self.cleaned_data.get('phone_number')
		if phone_number:
			if self.user_instance:
				if User.objects.filter(phone_number=phone_number).exclude(pk=self.user_instance.pk).exists():
					raise forms.ValidationError("A user with this phone number already exists.")
			else:
				if User.objects.filter(phone_number=phone_number).exists():
					raise forms.ValidationError("A user with this phone number already exists.")
		return phone_number

	def clean_password1(self):
		password1 = self.cleaned_data.get('password1')
		if password1:
			try:
				validate_password(password1)
			except ValidationError as e:
				raise forms.ValidationError(e)
		return password1

	def clean_password2(self):
		password1 = self.cleaned_data.get('password1')
		password2 = self.cleaned_data.get('password2')
		
		# Eğer password1 girilmişse password2 de girilmeli
		if password1 and not password2:
			raise forms.ValidationError("Please confirm your new password.")
		
		# Eğer password2 girilmişse password1 de girilmeli
		if password2 and not password1:
			raise forms.ValidationError("Please enter your new password first.")
		
		# Her ikisi de girildiyse eşleşmeli
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("The two password fields didn't match.")
		
		return password2

	def save(self, commit=True):
		user = super().save(commit=False)
		password = self.cleaned_data.get('password1')
		
		# Eğer yeni şifre girildiyse güncelle
		if password:
			user.set_password(password)
		
		if commit:
			user.save()
		return user


class AgentCreateForm(forms.ModelForm):
	email = forms.EmailField(
		required=True,
		widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
		help_text='Email address is required'
	)
	phone_number = PhoneNumberField(
		required=True,
		widget=PhoneNumberWidget(),
		help_text="Select your country and enter your phone number (required)"
	)
	password1 = forms.CharField(
		label='Password',
		widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
		required=True,
		help_text='<ul><li>At least 8 characters</li><li>Cannot be entirely numeric</li><li>Cannot be too common (like "password123")</li><li>Cannot be too similar to your username or email</li></ul>'
	)
	password2 = forms.CharField(
		label='Confirm Password',
		widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
		required=True,
		help_text='Enter the same password as above, for verification'
	)

	class Meta:
		model = User
		fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender')
		widgets = {
			'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
			'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
			'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
			'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
		}

	def clean_email(self):
		email = self.cleaned_data.get('email')
		if User.objects.filter(email=email).exists():
			raise forms.ValidationError("A user with this email already exists.")
		return email

	def clean_username(self):
		username = self.cleaned_data.get('username')
		if User.objects.filter(username=username).exists():
			raise forms.ValidationError("A user with this username already exists.")
		return username
	
	def clean_phone_number(self):
		phone_number = self.cleaned_data.get('phone_number')
		if phone_number and User.objects.filter(phone_number=phone_number).exists():
			raise forms.ValidationError("A user with this phone number already exists.")
		return phone_number

	def clean_password1(self):
		password1 = self.cleaned_data.get('password1')
		if password1:
			try:
				validate_password(password1)
			except ValidationError as e:
				raise forms.ValidationError(e)
		return password1

	def clean_password2(self):
		password1 = self.cleaned_data.get('password1')
		password2 = self.cleaned_data.get('password2')
		
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("The two password fields didn't match.")
		
		return password2

	def save(self, commit=True):
		user = super().save(commit=False)
		password = self.cleaned_data.get('password1')
		user.set_password(password)
		
		if commit:
			user.save()
		return user


class AdminAgentCreateForm(forms.ModelForm):
	email = forms.EmailField(
		required=True,
		widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
		help_text='Email address is required'
	)
	phone_number = PhoneNumberField(
		required=True,
		widget=PhoneNumberWidget(),
		help_text="Select your country and enter your phone number (required)"
	)
	organisation = forms.ModelChoiceField(
		queryset=UserProfile.objects.filter(
			user__is_organisor=True,
			user__is_superuser=False
		),
		empty_label="Select Organisation",
		widget=forms.Select(attrs={'class': 'form-control'})
	)
	password1 = forms.CharField(
		label='Password',
		widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
		required=True,
		help_text='<ul><li>At least 8 characters</li><li>Cannot be entirely numeric</li><li>Cannot be too common (like "password123")</li><li>Cannot be too similar to your username or email</li></ul>'
	)
	password2 = forms.CharField(
		label='Confirm Password',
		widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
		required=True,
		help_text='Enter the same password as above, for verification'
	)

	class Meta:
		model = User
		fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender', 'organisation')
		widgets = {
			'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
			'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
			'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
			'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
		}

	def clean_email(self):
		email = self.cleaned_data.get('email')
		if User.objects.filter(email=email).exists():
			raise forms.ValidationError("A user with this email already exists.")
		return email

	def clean_username(self):
		username = self.cleaned_data.get('username')
		if User.objects.filter(username=username).exists():
			raise forms.ValidationError("A user with this username already exists.")
		return username
	
	def clean_phone_number(self):
		phone_number = self.cleaned_data.get('phone_number')
		if phone_number and User.objects.filter(phone_number=phone_number).exists():
			raise forms.ValidationError("A user with this phone number already exists.")
		return phone_number

	def clean_password1(self):
		password1 = self.cleaned_data.get('password1')
		if password1:
			try:
				validate_password(password1)
			except ValidationError as e:
				raise forms.ValidationError(e)
		return password1

	def clean_password2(self):
		password1 = self.cleaned_data.get('password1')
		password2 = self.cleaned_data.get('password2')
		
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("The two password fields didn't match.")
		
		return password2

	def save(self, commit=True):
		user = super().save(commit=False)
		password = self.cleaned_data.get('password1')
		user.set_password(password)
		
		if commit:
			user.save()
		return user