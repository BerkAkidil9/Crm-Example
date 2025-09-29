from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField, AuthenticationForm
from .models import Lead, Agent, SourceCategory, ValueCategory, UserProfile

User = get_user_model()

class LeadModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super(LeadModelForm, self).__init__(*args, **kwargs)
        
        if request:
            user = request.user
            
            if user.is_organisor:
                # Organisor için kendi organizasyonunun kategorilerini ve agentlarını filtrele
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
                # Agent için kendi organizasyonunun kategorilerini ve agentlarını filtrele
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
                # Admin için tüm kategoriler ve agentlar
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


class AdminLeadModelForm(forms.ModelForm):
    organisation = forms.ModelChoiceField(
        queryset=UserProfile.objects.filter(
            user__is_organisor=True,
            user__is_superuser=False
        ),
        empty_label="Select Organisation",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super(AdminLeadModelForm, self).__init__(*args, **kwargs)
        
        # Başlangıçta boş queryset'ler
        self.fields["agent"].queryset = Agent.objects.none()
        self.fields["source_category"].queryset = SourceCategory.objects.none()
        self.fields["value_category"].queryset = ValueCategory.objects.none()
        
        # Eğer organizasyon seçilmişse (update durumunda), o organizasyonun verilerini yükle
        if self.instance and hasattr(self.instance, 'organisation') and self.instance.organisation:
            org = self.instance.organisation
            self.fields["agent"].queryset = Agent.objects.filter(organisation=org)
            self.fields["source_category"].queryset = SourceCategory.objects.filter(organisation=org)
            self.fields["value_category"].queryset = ValueCategory.objects.filter(organisation=org)
    
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


class LeadForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    age = forms.IntegerField(min_value=0)



class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=30)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
        field_classes = {'username': UsernameField}
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email



class AssignAgentForm(forms.Form):
    agent=forms.ModelChoiceField(queryset=Agent.objects.none())

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        agents = Agent.objects.filter(organisation=request.user.userprofile)
        super(AssignAgentForm, self).__init__(*args, **kwargs)
        self.fields["agent"].queryset = agents

class LeadCategoryUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super(LeadCategoryUpdateForm, self).__init__(*args, **kwargs)
        
        if request:
            user = request.user
            
            if user.is_organisor:
                try:
                    organisation = user.userprofile
                    self.fields["source_category"].queryset = SourceCategory.objects.filter(organisation=organisation)
                    self.fields["value_category"].queryset = ValueCategory.objects.filter(organisation=organisation)
                except Exception as e:
                    self.fields["source_category"].queryset = SourceCategory.objects.all()
                    self.fields["value_category"].queryset = ValueCategory.objects.all()
            elif user.is_agent:
                try:
                    organisation = user.agent.organisation
                    self.fields["source_category"].queryset = SourceCategory.objects.filter(organisation=organisation)
                    self.fields["value_category"].queryset = ValueCategory.objects.filter(organisation=organisation)
                except Exception as e:
                    self.fields["source_category"].queryset = SourceCategory.objects.all()
                    self.fields["value_category"].queryset = ValueCategory.objects.all()
            elif user.is_superuser or user.id == 1 or user.username == 'berk':
                self.fields["source_category"].queryset = SourceCategory.objects.all()
                self.fields["value_category"].queryset = ValueCategory.objects.all()
            else:
                self.fields["source_category"].queryset = SourceCategory.objects.all()
                self.fields["value_category"].queryset = ValueCategory.objects.all()
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
        # Error mesajlarını kaldır
        self.fields['username'].error_messages = {'required': ''}
        self.fields['password'].error_messages = {'required': ''}
        
        # Password field için de styling ekle
        self.fields['password'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Password'
        })