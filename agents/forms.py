from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from leads.models import UserProfile
from phonenumber_field.formfields import PhoneNumberField
from leads.forms import PhoneNumberWidget

User = get_user_model()

class AgentModelForm(forms.ModelForm):
	"""Agent my profile: all fields required except password; profile_image optional on update."""
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
	profile_image = forms.FileField(
		required=False,
		widget=forms.FileInput(attrs={
			'class': 'form-control',
			'accept': 'image/*',
			'id': 'id_profile_image',
		}),
		help_text='Upload a new profile photo. Leave empty to keep current. JPG, PNG, GIF, WebP. Max 5 MB.'
	)
	password1 = forms.CharField(
		label='New Password',
		widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'}),
		required=False,
		help_text='Leave blank to keep current password. If changing: at least 8 characters, not entirely numeric.'
	)
	password2 = forms.CharField(
		label='Confirm New Password',
		widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}),
		required=False,
		help_text='Enter the same password as above. Leave blank to keep current password.'
	)

	class Meta:
		model = User
		fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender', 'profile_image')
		widgets = {
			'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
			'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
			'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
			'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
		}

	def __init__(self, *args, **kwargs):
		self.user_instance = kwargs.get('instance')
		super().__init__(*args, **kwargs)
		# Agent my profile: all fields required except password and profile_image (optional on update)
		for f in ('username', 'first_name', 'last_name', 'date_of_birth', 'gender'):
			if f in self.fields:
				self.fields[f].required = True

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
		
		# If password1 is entered, password2 must be entered too
		if password1 and not password2:
			raise forms.ValidationError("Please confirm your new password.")
		
		# If password2 is entered, password1 must be entered too
		if password2 and not password1:
			raise forms.ValidationError("Please enter your new password first.")
		
		# If both are entered they must match
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("The two password fields didn't match.")
		
		return password2

	def clean_profile_image(self):
		upload = self.cleaned_data.get('profile_image')
		if upload and isinstance(upload, UploadedFile):
			allowed = ('image/jpeg', 'image/png', 'image/gif', 'image/webp')
			if getattr(upload, 'content_type', None) not in allowed:
				raise forms.ValidationError('Please upload a valid image (JPG, PNG, GIF or WebP).')
			if upload.size > 5 * 1024 * 1024:
				raise forms.ValidationError('File size must be less than 5 MB.')
		return upload

	def save(self, commit=True):
		user = super().save(commit=False)
		new_image = self.cleaned_data.get('profile_image')
		if new_image and isinstance(new_image, UploadedFile):
			user.profile_image = new_image
		password = self.cleaned_data.get('password1')
		if password:
			user.set_password(password)
		if commit:
			user.save()
		return user


class AdminAgentModelForm(forms.ModelForm):
	"""Admin-only agent update form: all fields required including profile_image."""
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
	profile_image = forms.FileField(
		required=False,
		widget=forms.FileInput(attrs={
			'class': 'form-control',
			'accept': 'image/*',
			'id': 'id_profile_image'
		}),
		help_text='Upload a new profile photo to change. Leave empty to keep current. JPG, PNG, GIF, WebP. Max 5 MB.'
	)
	password1 = forms.CharField(
		label='New Password',
		widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'}),
		required=False,
		help_text='Leave blank to keep current password.'
	)
	password2 = forms.CharField(
		label='Confirm New Password',
		widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}),
		required=False,
		help_text='Enter the same password as above, for verification'
	)
	organisation = forms.ModelChoiceField(
		queryset=UserProfile.objects.filter(
			user__is_organisor=True,
			user__is_superuser=False
		).order_by('user__username'),
		empty_label="Select Organisation",
		widget=forms.Select(attrs={'class': 'form-control'}),
		required=True,
		help_text='Select the organisation for this agent'
	)

	class Meta:
		model = User
		fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender', 'profile_image')
		widgets = {
			'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
			'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
			'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
			'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
		}

	def __init__(self, *args, **kwargs):
		self.agent = kwargs.pop('agent', None)
		self.user_instance = kwargs.get('instance')
		super().__init__(*args, **kwargs)
		for f in ('username', 'first_name', 'last_name', 'date_of_birth', 'gender'):
			self.fields[f].required = True
		if self.agent:
			self.fields['organisation'].initial = self.agent.organisation

	def clean_profile_image(self):
		upload = self.cleaned_data.get('profile_image')
		# Only validate when user uploaded a NEW file; skip validation for existing image (leave empty to keep)
		if upload and isinstance(upload, UploadedFile):
			allowed = ('image/jpeg', 'image/png', 'image/gif', 'image/webp')
			if getattr(upload, 'content_type', None) not in allowed:
				raise forms.ValidationError('Please upload a valid image (JPG, PNG, GIF or WebP).')
			if upload.size > 5 * 1024 * 1024:
				raise forms.ValidationError('File size must be less than 5 MB.')
		return upload

	def save(self, commit=True):
		user = super().save(commit=False)
		new_image = self.cleaned_data.get('profile_image')
		if new_image and isinstance(new_image, UploadedFile):
			user.profile_image = new_image
		password = self.cleaned_data.get('password1')
		if password:
			user.set_password(password)
		if commit:
			user.save()
		return user

	def clean_email(self):
		email = self.cleaned_data.get('email')
		if self.user_instance and User.objects.filter(email=email).exclude(pk=self.user_instance.pk).exists():
			raise forms.ValidationError("A user with this email already exists.")
		return email

	def clean_username(self):
		username = self.cleaned_data.get('username')
		if self.user_instance and User.objects.filter(username=username).exclude(pk=self.user_instance.pk).exists():
			raise forms.ValidationError("A user with this username already exists.")
		return username

	def clean_phone_number(self):
		phone_number = self.cleaned_data.get('phone_number')
		if phone_number and self.user_instance and User.objects.filter(phone_number=phone_number).exclude(pk=self.user_instance.pk).exists():
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
		if password1 and not password2:
			raise forms.ValidationError("Please confirm your new password.")
		if password2 and not password1:
			raise forms.ValidationError("Please enter your new password first.")
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("The two password fields didn't match.")
		return password2


class OrganisorAgentModelForm(forms.ModelForm):
	"""Organisor agent update: all fields required, profile photo update optional (leave empty to keep current)."""
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
	profile_image = forms.FileField(
		required=False,
		widget=forms.FileInput(attrs={
			'class': 'form-control',
			'accept': 'image/*',
			'id': 'id_profile_image'
		}),
		help_text='Upload a new profile photo to change. Leave empty to keep current. JPG, PNG, GIF, WebP. Max 5 MB.'
	)
	password1 = forms.CharField(
		label='New Password',
		widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'}),
		required=False,
		help_text='Leave blank to keep current password.'
	)
	password2 = forms.CharField(
		label='Confirm New Password',
		widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}),
		required=False,
		help_text='Enter the same password as above, for verification'
	)

	class Meta:
		model = User
		fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender', 'profile_image')
		widgets = {
			'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
			'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
			'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
			'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
		}

	def __init__(self, *args, **kwargs):
		self.user_instance = kwargs.get('instance')
		super().__init__(*args, **kwargs)
		for f in ('username', 'first_name', 'last_name', 'date_of_birth', 'gender'):
			self.fields[f].required = True

	def clean_profile_image(self):
		upload = self.cleaned_data.get('profile_image')
		if upload and isinstance(upload, UploadedFile):
			allowed = ('image/jpeg', 'image/png', 'image/gif', 'image/webp')
			if getattr(upload, 'content_type', None) not in allowed:
				raise forms.ValidationError('Please upload a valid image (JPG, PNG, GIF or WebP).')
			if upload.size > 5 * 1024 * 1024:
				raise forms.ValidationError('File size must be less than 5 MB.')
		return upload

	def save(self, commit=True):
		user = super().save(commit=False)
		new_image = self.cleaned_data.get('profile_image')
		if new_image and isinstance(new_image, UploadedFile):
			user.profile_image = new_image
		password = self.cleaned_data.get('password1')
		if password:
			user.set_password(password)
		if commit:
			user.save()
		return user

	def clean_email(self):
		email = self.cleaned_data.get('email')
		if self.user_instance and User.objects.filter(email=email).exclude(pk=self.user_instance.pk).exists():
			raise forms.ValidationError("A user with this email already exists.")
		return email

	def clean_username(self):
		username = self.cleaned_data.get('username')
		if self.user_instance and User.objects.filter(username=username).exclude(pk=self.user_instance.pk).exists():
			raise forms.ValidationError("A user with this username already exists.")
		return username

	def clean_phone_number(self):
		phone_number = self.cleaned_data.get('phone_number')
		if phone_number and self.user_instance and User.objects.filter(phone_number=phone_number).exclude(pk=self.user_instance.pk).exists():
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
		if password1 and not password2:
			raise forms.ValidationError("Please confirm your new password.")
		if password2 and not password1:
			raise forms.ValidationError("Please enter your new password first.")
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("The two password fields didn't match.")
		return password2


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


class OrganisorAgentCreateForm(forms.ModelForm):
	"""Organisor creates agent: all fields required including profile photo."""
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
	profile_image = forms.FileField(
		required=True,
		widget=forms.FileInput(attrs={
			'class': 'form-control',
			'accept': 'image/*',
			'id': 'id_profile_image'
		}),
		help_text='Upload a profile photo for the agent (required). Accepted: JPG, PNG, GIF, WebP. Max 5 MB.'
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
		fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender', 'profile_image')
		widgets = {
			'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
			'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
			'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
			'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for f in ('username', 'first_name', 'last_name', 'date_of_birth', 'gender'):
			self.fields[f].required = True

	def clean_profile_image(self):
		upload = self.cleaned_data.get('profile_image')
		if upload:
			allowed = ('image/jpeg', 'image/png', 'image/gif', 'image/webp')
			if getattr(upload, 'content_type', None) not in allowed:
				raise forms.ValidationError('Please upload a valid image (JPG, PNG, GIF or WebP).')
			if upload.size > 5 * 1024 * 1024:
				raise forms.ValidationError('File size must be less than 5 MB.')
		return upload

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
		widget=forms.Select(attrs={'class': 'form-control'}),
		required=True,
		help_text='Select the organisation for this agent (required)'
	)
	profile_image = forms.FileField(
		required=True,
		widget=forms.FileInput(attrs={
			'class': 'form-control',
			'accept': 'image/*',
			'id': 'id_profile_image'
		}),
		help_text='Upload a profile photo for the agent (required). Accepted: JPG, PNG, GIF, WebP.'
	)

	def clean_profile_image(self):
		upload = self.cleaned_data.get('profile_image')
		if upload:
			allowed = ('image/jpeg', 'image/png', 'image/gif', 'image/webp')
			if getattr(upload, 'content_type', None) not in allowed:
				raise forms.ValidationError('Please upload a valid image (JPG, PNG, GIF or WebP).')
			if upload.size > 5 * 1024 * 1024:  # 5 MB
				raise forms.ValidationError('File size must be less than 5 MB.')
		return upload
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
		fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender', 'organisation', 'profile_image')
		widgets = {
			'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
			'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
			'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
			'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# All fields required when admin creates an agent
		self.fields['date_of_birth'].required = True
		self.fields['gender'].required = True
		self.fields['username'].required = True
		self.fields['first_name'].required = True
		self.fields['last_name'].required = True

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