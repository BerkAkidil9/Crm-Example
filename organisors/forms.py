from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from phonenumber_field.formfields import PhoneNumberField
from leads.forms import PhoneNumberWidget, validate_image_upload

User = get_user_model()

class OrganisorModelForm(forms.ModelForm):
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
        help_text='Leave blank to keep your current password. If changing: at least 8 characters, not entirely numeric, not too common.'
    )
    password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}),
        required=False,
        help_text='Enter the same password as above, for verification. Leave blank to keep current password.'
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender', 'profile_image')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'id': 'id_profile_image'}),
        }

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        for field_name in ('username', 'first_name', 'last_name', 'date_of_birth', 'gender'):
            if field_name in self.fields:
                self.fields[field_name].required = True
        if self.fields.get('profile_image'):
            if self.user_instance and self.user_instance.pk and getattr(self.user_instance, 'profile_image', None) and self.user_instance.profile_image:
                self.fields['profile_image'].required = False
                self.fields['profile_image'].help_text = 'Upload a new photo to change, or leave empty to keep current. JPG, PNG, GIF, WebP. Max 5 MB.'
            else:
                self.fields['profile_image'].required = True

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
            validate_image_upload(upload)
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


class OrganisorCreateForm(forms.ModelForm):
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
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender', 'profile_image')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'id': 'id_profile_image'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ('username', 'first_name', 'last_name', 'date_of_birth', 'gender', 'profile_image'):
            if field_name in self.fields:
                self.fields[field_name].required = True

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

    def clean_profile_image(self):
        upload = self.cleaned_data.get('profile_image')
        if upload and isinstance(upload, UploadedFile):
            validate_image_upload(upload)
        return upload

    def save(self, commit=True):
        user = super().save(commit=False)
        new_image = self.cleaned_data.get('profile_image')
        if new_image and isinstance(new_image, UploadedFile):
            user.profile_image = new_image
        password = self.cleaned_data.get('password1')
        user.set_password(password)
        
        if commit:
            user.save()
        return user
