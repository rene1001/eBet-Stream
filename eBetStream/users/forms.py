# users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.core.validators import MinLengthValidator
from .models import User, Transaction, PaymentMethod, DepositRequest, WithdrawalRequest, GameOrganizationRequest
from django.utils import timezone

class UserRegisterForm(UserCreationForm):
    """Custom registration form"""
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class AdminRegisterForm(UserCreationForm):
    """Administrator registration form"""
    email = forms.EmailField(required=True)
    invitation_code = forms.CharField(
        max_length=20, 
        required=True,
        help_text="Invitation code required to create an administrator account."
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'invitation_code', 'password1', 'password2']

    def clean_invitation_code(self):
        invitation_code = self.cleaned_data.get('invitation_code')
        # Check if the invitation code is valid
        if invitation_code != 'ADMIN2024':  # Fixed invitation code for example
            raise forms.ValidationError("Invalid invitation code.")
        return invitation_code


class UserLoginForm(AuthenticationForm):
    """Custom login form"""
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput,
    )


class UserUpdateForm(forms.ModelForm):
    """Profile update form"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_picture', 'language']


class DepositForm(forms.ModelForm):
    """Deposit form"""
    amount = forms.DecimalField(
        min_value=5,
        max_value=1000,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Minimum amount: 5'})
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('credit_card', 'Credit Card'),
            ('paypal', 'PayPal'),
            ('crypto', 'Cryptocurrency'),
        ],
        widget=forms.RadioSelect
    )

    class Meta:
        model = Transaction
        fields = ['amount', 'payment_method']


class WithdrawalForm(forms.ModelForm):
    """Withdrawal form"""
    amount = forms.DecimalField(
        min_value=10,
        max_value=1000,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Minimum amount: 10.00 Ktap / Maximum: 1000.00 Ktap'})
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('bank_transfer', 'Bank Transfer'),
            ('paypal', 'PayPal'),
            ('crypto', 'Cryptocurrency'),
        ],
        widget=forms.RadioSelect
    )

    class Meta:
        model = Transaction
        fields = ['amount', 'payment_method']


class DepositRequestForm(forms.ModelForm):
    """Deposit request form"""
    amount = forms.DecimalField(
        min_value=5,
        max_value=1000,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Minimum amount: 5'})
    )
    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.filter(is_active=True),
        empty_label=None,
        widget=forms.RadioSelect
    )
    proof_of_payment = forms.ImageField(
        required=False,
        label="Payment Proof",
        help_text="Attach a screenshot or photo of your payment proof"
    )

    class Meta:
        model = DepositRequest
        fields = ['amount', 'payment_method', 'proof_of_payment']
        
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        payment_method = self.cleaned_data.get('payment_method')
        
        if payment_method and amount:
            if amount < payment_method.min_amount:
                raise forms.ValidationError(f"Minimum amount for {payment_method.name} is {payment_method.min_amount}")
            if amount > payment_method.max_amount:
                raise forms.ValidationError(f"Maximum amount for {payment_method.name} is {payment_method.max_amount}")
        
        return amount

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('profile_picture', 'language')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = UserChangeForm.Meta.fields

class WithdrawalRequestForm(forms.ModelForm):
    """Withdrawal request form"""
    amount = forms.DecimalField(
        min_value=10,
        max_value=1000,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Minimum amount: 10.00 Ktap / Maximum: 1000.00 Ktap'})
    )
    
    class Meta:
        model = WithdrawalRequest
        fields = [
            'amount',
            'payment_method',
            'reference_paiement',
            'paypal_email',
            'crypto_address',
        ]
        widgets = {
            'reference_paiement': forms.HiddenInput(),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'paypal_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your PayPal email address'}),
            'crypto_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your crypto wallet address'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make conditional fields not required by default
        self.fields['paypal_email'].required = False
        self.fields['crypto_address'].required = False
        
        # Add more descriptive labels
        self.fields['payment_method'].label = "Payment Method"
        self.fields['crypto_address'].label = "Crypto Wallet Address"
        self.fields['paypal_email'].label = "PayPal Email"
    
    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        payment_method = cleaned_data.get('payment_method')
        
        # Balance validation directly in the form
        user = self.initial.get('user') # Get the user passed from the view
        if user and amount is not None:
            user_balance = user.kapanga_balance if user.kapanga_balance is not None else 0
            if amount > user_balance:
                raise forms.ValidationError('Insufficient Ktap balance to make this withdrawal.')
        
        # Payment reference validation based on chosen method
        if payment_method == 'crypto':
            crypto_address = cleaned_data.get('crypto_address')
            if not crypto_address:
                self.add_error('crypto_address', 'Please provide a crypto wallet address.')
            else:
                # Store crypto address in reference_paiement field
                cleaned_data['reference_paiement'] = crypto_address
        
        elif payment_method == 'paypal':
            paypal_email = cleaned_data.get('paypal_email')
            if not paypal_email:
                self.add_error('paypal_email', 'Please provide a PayPal email address.')
            else:
                # Store PayPal email in reference_paiement field
                cleaned_data['reference_paiement'] = paypal_email
        
        elif payment_method == 'bank':
            bank_name = cleaned_data.get('bank_name')
            iban = cleaned_data.get('iban')
            if not bank_name or not iban:
                if not bank_name:
                    self.add_error('bank_name', 'Please provide your bank name.')
                if not iban:
                    self.add_error('iban', 'Please provide your IBAN.')
                
        return cleaned_data
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than 0.")

class GameOrganizationRequestForm(forms.ModelForm):
    """Game organization request form"""
    game_name = forms.CharField(max_length=200, label="Proposed Game Name")
    description = forms.CharField(widget=forms.Textarea, label="Request Details")

    class Meta:
        model = GameOrganizationRequest
        fields = ['game_name', 'description']