from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.core.files.uploadedfile import UploadedFile
from .models import Lead, Agent, SourceCategory, ValueCategory, UserProfile
from phonenumber_field.formfields import PhoneNumberField

class PhoneNumberWidget(forms.MultiWidget):
    """Custom widget for phone number with country code dropdown"""
    
    def __init__(self, attrs=None):
        country_choices = [
            ('+90', '\U0001F1F9\U0001F1F7 Turkey (+90)'),
            ('+1', '\U0001F1FA\U0001F1F8 United States (+1)'),
            ('+44', '\U0001F1EC\U0001F1E7 United Kingdom (+44)'),
            ('+49', '\U0001F1E9\U0001F1EA Germany (+49)'),
            ('+33', '\U0001F1EB\U0001F1F7 France (+33)'),
            ('+39', '\U0001F1EE\U0001F1F9 Italy (+39)'),
            ('+34', '\U0001F1EA\U0001F1F8 Spain (+34)'),
            ('+31', '\U0001F1F3\U0001F1F1 Netherlands (+31)'),
            ('+7', '\U0001F1F7\U0001F1FA Russia (+7)'),
            ('+86', '\U0001F1E8\U0001F1F3 China (+86)'),
            ('+91', '\U0001F1EE\U0001F1F3 India (+91)'),
            ('+81', '\U0001F1EF\U0001F1F5 Japan (+81)'),
            ('+82', '\U0001F1F0\U0001F1F7 South Korea (+82)'),
            ('+55', '\U0001F1E7\U0001F1F7 Brazil (+55)'),
            ('+52', '\U0001F1F2\U0001F1FD Mexico (+52)'),
            ('+61', '\U0001F1E6\U0001F1FA Australia (+61)'),
            ('+64', '\U0001F1F3\U0001F1FF New Zealand (+64)'),
            ('+27', '\U0001F1FF\U0001F1E6 South Africa (+27)'),
            ('+20', '\U0001F1EA\U0001F1EC Egypt (+20)'),
            ('+966', '\U0001F1F8\U0001F1E6 Saudi Arabia (+966)'),
            ('+971', '\U0001F1E6\U0001F1EA UAE (+971)'),
            ('+972', '\U0001F1EE\U0001F1F1 Israel (+972)'),
            ('+98', '\U0001F1EE\U0001F1F7 Iran (+98)'),
            ('+92', '\U0001F1F5\U0001F1F0 Pakistan (+92)'),
            ('+880', '\U0001F1E7\U0001F1E9 Bangladesh (+880)'),
            ('+66', '\U0001F1F9\U0001F1ED Thailand (+66)'),
            ('+84', '\U0001F1FB\U0001F1F3 Vietnam (+84)'),
            ('+60', '\U0001F1F2\U0001F1FE Malaysia (+60)'),
            ('+65', '\U0001F1F8\U0001F1EC Singapore (+65)'),
            ('+62', '\U0001F1EE\U0001F1E9 Indonesia (+62)'),
            ('+63', '\U0001F1F5\U0001F1ED Philippines (+63)'),
            ('+32', '\U0001F1E7\U0001F1EA Belgium (+32)'),
            ('+41', '\U0001F1E8\U0001F1ED Switzerland (+41)'),
            ('+43', '\U0001F1E6\U0001F1F9 Austria (+43)'),
            ('+45', '\U0001F1E9\U0001F1F0 Denmark (+45)'),
            ('+46', '\U0001F1F8\U0001F1EA Sweden (+46)'),
            ('+47', '\U0001F1F3\U0001F1F4 Norway (+47)'),
            ('+358', '\U0001F1EB\U0001F1EE Finland (+358)'),
            ('+48', '\U0001F1F5\U0001F1F1 Poland (+48)'),
            ('+420', '\U0001F1E8\U0001F1FF Czech Republic (+420)'),
            ('+421', '\U0001F1F8\U0001F1F0 Slovakia (+421)'),
            ('+36', '\U0001F1ED\U0001F1FA Hungary (+36)'),
            ('+40', '\U0001F1F7\U0001F1F4 Romania (+40)'),
            ('+359', '\U0001F1E7\U0001F1EC Bulgaria (+359)'),
            ('+385', '\U0001F1ED\U0001F1F7 Croatia (+385)'),
            ('+381', '\U0001F1F7\U0001F1F8 Serbia (+381)'),
            ('+30', '\U0001F1EC\U0001F1F7 Greece (+30)'),
            ('+351', '\U0001F1F5\U0001F1F9 Portugal (+351)'),
            ('+353', '\U0001F1EE\U0001F1EA Ireland (+353)'),
            ('+370', '\U0001F1F1\U0001F1F9 Lithuania (+370)'),
            ('+371', '\U0001F1F1\U0001F1FB Latvia (+371)'),
            ('+372', '\U0001F1EA\U0001F1EA Estonia (+372)'),
            ('+374', '\U0001F1E6\U0001F1F2 Armenia (+374)'),
            ('+995', '\U0001F1EC\U0001F1EA Georgia (+995)'),
            ('+994', '\U0001F1E6\U0001F1FF Azerbaijan (+994)'),
            ('+993', '\U0001F1F9\U0001F1F2 Turkmenistan (+993)'),
            ('+992', '\U0001F1F9\U0001F1EF Tajikistan (+992)'),
            ('+996', '\U0001F1F0\U0001F1EC Kyrgyzstan (+996)'),
            ('+998', '\U0001F1FA\U0001F1FF Uzbekistan (+998)'),
            ('+77', '\U0001F1F0\U0001F1FF Kazakhstan (+77)'),
            ('+375', '\U0001F1E7\U0001F1FE Belarus (+375)'),
            ('+380', '\U0001F1FA\U0001F1E6 Ukraine (+380)'),
            ('+373', '\U0001F1F2\U0001F1E9 Moldova (+373)'),
            ('+212', '\U0001F1F2\U0001F1E6 Morocco (+212)'),
            ('+213', '\U0001F1E9\U0001F1FF Algeria (+213)'),
            ('+216', '\U0001F1F9\U0001F1F3 Tunisia (+216)'),
            ('+218', '\U0001F1F1\U0001F1FE Libya (+218)'),
            ('+251', '\U0001F1EA\U0001F1F9 Ethiopia (+251)'),
            ('+254', '\U0001F1F0\U0001F1EA Kenya (+254)'),
            ('+255', '\U0001F1F9\U0001F1FF Tanzania (+255)'),
            ('+256', '\U0001F1FA\U0001F1EC Uganda (+256)'),
            ('+234', '\U0001F1F3\U0001F1EC Nigeria (+234)'),
            ('+233', '\U0001F1EC\U0001F1ED Ghana (+233)'),
            ('+225', '\U0001F1E8\U0001F1EE Ivory Coast (+225)'),
            ('+221', '\U0001F1F8\U0001F1F3 Senegal (+221)'),
            ('+502', '\U0001F1EC\U0001F1F9 Guatemala (+502)'),
            ('+503', '\U0001F1F8\U0001F1FB El Salvador (+503)'),
            ('+504', '\U0001F1ED\U0001F1F3 Honduras (+504)'),
            ('+505', '\U0001F1F3\U0001F1EE Nicaragua (+505)'),
            ('+506', '\U0001F1E8\U0001F1F7 Costa Rica (+506)'),
            ('+507', '\U0001F1F5\U0001F1E6 Panama (+507)'),
            ('+56', '\U0001F1E8\U0001F1F1 Chile (+56)'),
            ('+54', '\U0001F1E6\U0001F1F7 Argentina (+54)'),
            ('+51', '\U0001F1F5\U0001F1EA Peru (+51)'),
            ('+57', '\U0001F1E8\U0001F1F4 Colombia (+57)'),
            ('+58', '\U0001F1FB\U0001F1EA Venezuela (+58)'),
            ('+593', '\U0001F1EA\U0001F1E8 Ecuador (+593)'),
            ('+595', '\U0001F1F5\U0001F1FE Paraguay (+595)'),
            ('+598', '\U0001F1FA\U0001F1FE Uruguay (+598)'),
            ('+591', '\U0001F1E7\U0001F1F4 Bolivia (+591)'),
        ]
        widgets = [
            forms.Select(choices=country_choices, attrs={
                'class': 'form-control', 
                'style': 'width: 180px; display: inline-block; font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif;'
            }),
            forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '555 123 4567', 
                'style': 'width: calc(100% - 190px); display: inline-block; margin-left: 5px;'
            })
        ]
        super().__init__(widgets, attrs)
    
    def decompress(self, value):
        if value:
            # Convert PhoneNumber to string if needed
            value_str = str(value) if value else ''
            if value_str.startswith('+'):
                # Split country code and number - check from longest code first
                country_codes = ['+966', '+971', '+972', '+880', '+358', '+420', '+421', '+359', '+385', '+381', '+351', '+353', '+370', '+371', '+372', '+374', '+995', '+994', '+993', '+992', '+996', '+998', '+375', '+380', '+373', '+212', '+213', '+216', '+218', '+251', '+254', '+255', '+256', '+234', '+233', '+225', '+221', '+502', '+503', '+504', '+505', '+506', '+507', '+593', '+595', '+598', '+591', '+90', '+44', '+49', '+33', '+39', '+34', '+31', '+91', '+81', '+82', '+55', '+52', '+61', '+64', '+27', '+20', '+98', '+92', '+66', '+84', '+60', '+65', '+62', '+63', '+32', '+41', '+43', '+45', '+46', '+47', '+48', '+36', '+40', '+30', '+77', '+56', '+54', '+51', '+57', '+58', '+7', '+1']
                
                # Find longest matching code
                for code in country_codes:
                    if value_str.startswith(code):
                        return [code, value_str[len(code):].strip()]
                return ['+90', value_str[1:]]  # Default to TR
            return ['+90', value_str]
        return ['+90', '']
    
    def value_from_datadict(self, data, files, name):
        country_code = data.get(name + '_0', '+90')
        phone_number = data.get(name + '_1', '')
        if phone_number:
            return country_code + phone_number.replace(' ', '').replace('-', '')
        return ''

User = get_user_model()

class LeadModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super(LeadModelForm, self).__init__(*args, **kwargs)
        
        if request:
            user = request.user
            
            if user.is_organisor:
                # Filter categories and agents for organisor's organisation
                try:
                    organisation = user.userprofile
                    self.fields["source_category"].queryset = SourceCategory.objects.filter(organisation=organisation)
                    self.fields["value_category"].queryset = ValueCategory.objects.filter(organisation=organisation)
                    self.fields["agent"].queryset = Agent.objects.filter(organisation=organisation)
                except Exception as e:
                    # Fallback to all categories and agents if error
                    self.fields["source_category"].queryset = SourceCategory.objects.all()
                    self.fields["value_category"].queryset = ValueCategory.objects.all()
                    self.fields["agent"].queryset = Agent.objects.all()
            elif user.is_agent:
                # Filter categories and agents for agent's organisation
                try:
                    organisation = user.agent.organisation
                    self.fields["source_category"].queryset = SourceCategory.objects.filter(organisation=organisation)
                    self.fields["value_category"].queryset = ValueCategory.objects.filter(organisation=organisation)
                    self.fields["agent"].queryset = Agent.objects.filter(organisation=organisation)
                except Exception as e:
                    # Fallback to all categories and agents if error
                    self.fields["source_category"].queryset = SourceCategory.objects.all()
                    self.fields["value_category"].queryset = ValueCategory.objects.all()
                    self.fields["agent"].queryset = Agent.objects.all()
            elif user.is_superuser:
                # Admin sees all categories and agents
                self.fields["source_category"].queryset = SourceCategory.objects.all()
                self.fields["value_category"].queryset = ValueCategory.objects.all()
                self.fields["agent"].queryset = Agent.objects.all()
            else:
                # Default fallback
                self.fields["source_category"].queryset = SourceCategory.objects.all()
                self.fields["value_category"].queryset = ValueCategory.objects.all()
                self.fields["agent"].queryset = Agent.objects.all()
        else:
            # Default queryset when no request
            self.fields["source_category"].queryset = SourceCategory.objects.all()
            self.fields["value_category"].queryset = ValueCategory.objects.all()
            self.fields["agent"].queryset = Agent.objects.all()
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # If updating existing instance, exclude self from check
            if self.instance and self.instance.pk:
                if Lead.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError("A lead with this email already exists.")
            else:
                # When creating new lead, check for duplicates
                if Lead.objects.filter(email=email).exists():
                    raise forms.ValidationError("A lead with this email already exists.")
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # If updating existing instance, exclude self from check
            if self.instance and self.instance.pk:
                if Lead.objects.filter(phone_number=phone_number).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError("A lead with this phone number already exists.")
            else:
                # When creating new lead, check for duplicates
                if Lead.objects.filter(phone_number=phone_number).exists():
                    raise forms.ValidationError("A lead with this phone number already exists.")
        return phone_number
    
    class Meta:
        model = Lead
        fields = [
            'first_name',
            'last_name',
            'age',
            'agent',
            'source_category',
            'value_category',
            'description',
            'phone_number',
            'email',
            'address',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 3}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
        }


class OrganisorLeadModelForm(forms.ModelForm):
    """Organisor lead create/update: profile photo required on create, optional on update (leave empty to keep)."""
    profile_image = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'id_lead_profile_image',
        }),
        help_text='Profil fotoğrafı (zorunlu). JPG, PNG, GIF, WebP. Max 5 MB.'
    )

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super(OrganisorLeadModelForm, self).__init__(*args, **kwargs)
        if request and request.user.is_organisor:
            try:
                organisation = request.user.userprofile
                self.fields["source_category"].queryset = SourceCategory.objects.filter(organisation=organisation)
                self.fields["value_category"].queryset = ValueCategory.objects.filter(organisation=organisation)
                self.fields["agent"].queryset = Agent.objects.filter(organisation=organisation)
            except Exception:
                self.fields["source_category"].queryset = SourceCategory.objects.all()
                self.fields["value_category"].queryset = ValueCategory.objects.all()
                self.fields["agent"].queryset = Agent.objects.all()
        else:
            self.fields["source_category"].queryset = SourceCategory.objects.all()
            self.fields["value_category"].queryset = ValueCategory.objects.all()
            self.fields["agent"].queryset = Agent.objects.all()
        if self.instance and self.instance.pk and self.instance.profile_image:
            self.fields['profile_image'].required = False
            self.fields['profile_image'].help_text = 'Yeni fotoğraf yükleyin veya mevcut kalsın. Boş bırakırsanız değişmez. JPG, PNG, GIF, WebP. Max 5 MB.'

    def clean_profile_image(self):
        upload = self.cleaned_data.get('profile_image')
        if upload and isinstance(upload, UploadedFile):
            allowed = ('image/jpeg', 'image/png', 'image/gif', 'image/webp')
            if getattr(upload, 'content_type', None) not in allowed:
                raise forms.ValidationError('Lütfen geçerli bir resim yükleyin (JPG, PNG, GIF veya WebP).')
            if upload.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Dosya boyutu 5 MB\'dan küçük olmalıdır.')
        elif not upload and (not self.instance or not self.instance.pk or not getattr(self.instance, 'profile_image', None) or not self.instance.profile_image):
            raise forms.ValidationError('Profil fotoğrafı zorunludur.')
        return upload

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if self.instance and self.instance.pk:
                if Lead.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError("Bu e-posta adresi zaten kullanılıyor.")
            else:
                if Lead.objects.filter(email=email).exists():
                    raise forms.ValidationError("Bu e-posta adresi zaten kullanılıyor.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            if self.instance and self.instance.pk:
                if Lead.objects.filter(phone_number=phone_number).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError("Bu telefon numarası zaten kullanılıyor.")
            else:
                if Lead.objects.filter(phone_number=phone_number).exists():
                    raise forms.ValidationError("Bu telefon numarası zaten kullanılıyor.")
        return phone_number

    def save(self, commit=True):
        lead = super().save(commit=False)
        new_image = self.cleaned_data.get('profile_image')
        if new_image and isinstance(new_image, UploadedFile):
            lead.profile_image = new_image
        if commit:
            lead.save()
        return lead

    class Meta:
        model = Lead
        fields = [
            'first_name',
            'last_name',
            'age',
            'agent',
            'source_category',
            'value_category',
            'description',
            'phone_number',
            'email',
            'address',
            'profile_image',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 3}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
        }


class AdminLeadModelForm(forms.ModelForm):
    organisation = forms.ModelChoiceField(
        queryset=UserProfile.objects.none(),  # Set fresh in __init__
        empty_label="Select Organisation",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    profile_image = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'id_lead_profile_image'
        }),
        help_text='Profile photo (required). JPG, PNG, GIF, WebP. Max 5 MB.'
    )

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super(AdminLeadModelForm, self).__init__(*args, **kwargs)
        # Her istekte tüm organisor'ları göster (2. organisor sonradan eklenmiş olsa da)
        self.fields['organisation'].queryset = UserProfile.objects.filter(
            user__is_organisor=True,
            user__is_superuser=False
        ).order_by('user__username')
        # On update, profile_image can be left empty to keep current
        if self.instance and self.instance.pk and self.instance.profile_image:
            self.fields['profile_image'].required = False
            self.fields['profile_image'].help_text = 'Upload a new photo to change. Leave empty to keep current. JPG, PNG, GIF, WebP. Max 5 MB.'
        # Start with empty querysets
        self.fields["agent"].queryset = Agent.objects.none()
        self.fields["source_category"].queryset = SourceCategory.objects.none()
        self.fields["value_category"].queryset = ValueCategory.objects.none()
        
        # Determine organisation: from instance (update), from submitted data (POST), or from initial (admin create GET)
        org = None
        if self.instance and hasattr(self.instance, 'organisation') and self.instance.organisation:
            org = self.instance.organisation
        elif self.data and self.data.get('organisation'):
            try:
                org = UserProfile.objects.get(pk=self.data.get('organisation'))
            except (ValueError, UserProfile.DoesNotExist):
                pass
        elif not self.instance or not self.instance.pk:
            # Admin create (GET): org can come from view's get_initial()
            org_id = self.initial.get('organisation') if self.initial else None
            if org_id:
                try:
                    org = UserProfile.objects.get(pk=org_id)
                except (ValueError, UserProfile.DoesNotExist):
                    pass
            if org is None:
                first_org = UserProfile.objects.filter(
                    user__is_organisor=True,
                    user__is_superuser=False
                ).order_by('user__username').first()
                if first_org:
                    org = first_org
                    self.initial.setdefault('organisation', org.pk)
                    self.fields['organisation'].initial = org.pk
        
        if org:
            # Varsayılan source ve value kategorilerini yoksa oluştur (sadece Unassigned değil, hepsi)
            _default_source = [
                "Website", "Social Media", "Email Campaign", "Cold Call", "Referral",
                "Trade Show", "Advertisement", "Direct Mail", "SEO/Google", "Unassigned"
            ]
            _default_value = [
                "Enterprise", "SMB", "Small Business", "Individual",
                "High Value", "Medium Value", "Low Value", "Unassigned"
            ]
            for name in _default_source:
                SourceCategory.objects.get_or_create(name=name, organisation=org)
            for name in _default_value:
                ValueCategory.objects.get_or_create(name=name, organisation=org)
            self.fields["agent"].queryset = Agent.objects.filter(organisation=org).select_related('user')
            self.fields["agent"].label_from_instance = lambda obj: f"{obj.user.get_full_name() or obj.user.username} ({obj.user.email})"
            self.fields["source_category"].queryset = SourceCategory.objects.filter(organisation=org)
            self.fields["value_category"].queryset = ValueCategory.objects.filter(organisation=org)

    def clean_profile_image(self):
        upload = self.cleaned_data.get('profile_image')
        if upload and isinstance(upload, UploadedFile):
            allowed = ('image/jpeg', 'image/png', 'image/gif', 'image/webp')
            if getattr(upload, 'content_type', None) not in allowed:
                raise forms.ValidationError('Please upload a valid image (JPG, PNG, GIF or WebP).')
            if upload.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size must be less than 5 MB.')
        elif not upload and (not self.instance or not self.instance.pk or not getattr(self.instance, 'profile_image', None) or not self.instance.profile_image):
            raise forms.ValidationError('Profile photo is required.')
        return upload
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # If updating existing instance, exclude self from check
            if self.instance and self.instance.pk:
                if Lead.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError("A lead with this email already exists.")
            else:
                # When creating new lead, check for duplicates
                if Lead.objects.filter(email=email).exists():
                    raise forms.ValidationError("A lead with this email already exists.")
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # If updating existing instance, exclude self from check
            if self.instance and self.instance.pk:
                if Lead.objects.filter(phone_number=phone_number).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError("A lead with this phone number already exists.")
            else:
                # When creating new lead, check for duplicates
                if Lead.objects.filter(phone_number=phone_number).exists():
                    raise forms.ValidationError("A lead with this phone number already exists.")
        return phone_number
    
    def save(self, commit=True):
        lead = super().save(commit=False)
        new_image = self.cleaned_data.get('profile_image')
        if new_image and isinstance(new_image, UploadedFile):
            lead.profile_image = new_image
        if commit:
            lead.save()
        return lead

    class Meta:
        model = Lead
        fields = [
            'first_name',
            'last_name', 
            'age',
            'organisation',
            'agent',
            'source_category',
            'value_category',
            'description',
            'phone_number',
            'email',
            'address',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 3}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
        }


class LeadForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    age = forms.IntegerField(min_value=0)



class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Email address is required",
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )
    first_name = forms.CharField(
        required=True, 
        max_length=30,
        help_text="First name is required",
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        required=True, 
        max_length=30,
        help_text="Last name is required",
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    phone_number = PhoneNumberField(
        required=True,
        widget=PhoneNumberWidget(),
        help_text="Select your country and enter your phone number"
    )
    date_of_birth = forms.DateField(
        required=True, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="Date of birth is required"
    )
    gender = forms.ChoiceField(required=True, choices=User.GENDER_CHOICES, help_text="Gender is required")
    profile_image = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={'accept': 'image/*', 'id': 'id_profile_image', 'class': 'form-control'}),
        help_text="Upload a profile picture (required)."
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "phone_number", "date_of_birth", "gender", "profile_image", "password1", "password2")
        field_classes = {'username': UsernameField}
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("A user with this phone number already exists.")
        return phone_number
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username



class AssignAgentForm(forms.Form):
    agent = forms.ModelChoiceField(queryset=Agent.objects.none())

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        lead = kwargs.pop("lead", None)
        super(AssignAgentForm, self).__init__(*args, **kwargs)
        if request.user.is_superuser and lead and getattr(lead, "organisation", None):
            agents = Agent.objects.filter(organisation=lead.organisation)
        elif getattr(request.user, "userprofile", None):
            agents = Agent.objects.filter(organisation=request.user.userprofile)
        else:
            agents = Agent.objects.none()
        self.fields["agent"].queryset = agents

class LeadCategoryUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super(LeadCategoryUpdateForm, self).__init__(*args, **kwargs)
        
        organisation = None
        if request:
            user = request.user
            if user.is_superuser and self.instance and getattr(self.instance, 'organisation', None):
                organisation = self.instance.organisation
            elif user.is_organisor:
                try:
                    organisation = user.userprofile
                except Exception:
                    pass
            elif user.is_agent:
                try:
                    organisation = user.agent.organisation
                except Exception:
                    pass
        if organisation:
            _default_source = [
                "Website", "Social Media", "Email Campaign", "Cold Call", "Referral",
                "Trade Show", "Advertisement", "Direct Mail", "SEO/Google", "Unassigned"
            ]
            _default_value = [
                "Enterprise", "SMB", "Small Business", "Individual",
                "High Value", "Medium Value", "Low Value", "Unassigned"
            ]
            for name in _default_source:
                SourceCategory.objects.get_or_create(name=name, organisation=organisation)
            for name in _default_value:
                ValueCategory.objects.get_or_create(name=name, organisation=organisation)
            self.fields["source_category"].queryset = SourceCategory.objects.filter(organisation=organisation)
            self.fields["value_category"].queryset = ValueCategory.objects.filter(organisation=organisation)
        else:
            self.fields["source_category"].queryset = SourceCategory.objects.all()
            self.fields["value_category"].queryset = ValueCategory.objects.all()

    class Meta:
        model = Lead
        fields = (
            'source_category',
            'value_category',
        )

class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': "Wrong username or password. Please try again.",
        'inactive': "This account is inactive.",
    }
    username = forms.CharField(
        label='Username or Email',
        max_length=254,
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'placeholder': 'Username or Email',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove default error messages
        self.fields['username'].error_messages = {'required': ''}
        self.fields['password'].error_messages = {'required': ''}
        
        # Add styling to password field
        self.fields['password'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Password'
        })

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='Email',
        max_length=254,
        widget=forms.EmailInput(attrs={
            'autofocus': True,
            'placeholder': 'Email',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
        })
    )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='New password',
        widget=forms.PasswordInput(attrs={
            'autofocus': True,
            'placeholder': 'New Password',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
        }),
        strip=False,
        help_text="Your password can't be too similar to your other personal information, must contain at least 8 characters, can't be a commonly used password, and can't be entirely numeric.",
    )
    
    new_password2 = forms.CharField(
        label='New password confirmation',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm New Password',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
        }),
    )