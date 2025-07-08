# users/views.py

from django.shortcuts import redirect, render
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views import generic
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib.auth.views import (
    PasswordChangeView as AuthPasswordChangeView,
    PasswordResetView as AuthPasswordResetView,
    PasswordResetDoneView as AuthPasswordResetDoneView,
    PasswordResetConfirmView as AuthPasswordResetConfirmView,
    PasswordResetCompleteView as AuthPasswordResetCompleteView,
)
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from .forms import UserRegisterForm, UserLoginForm, UserUpdateForm, DepositForm, WithdrawalForm, DepositRequestForm, AdminRegisterForm, WithdrawalRequestForm, GameOrganizationRequestForm
from .models import User, Transaction, UserActivity, PaymentMethod, DepositRequest, WithdrawalRequest, GameOrganizationRequest, PromoCode, PromoCodeUsage, KtapToken, VipSale, VipEvent, FidelityPoint, VipBonus, VIPRequest
from django.db import transaction as db_transaction
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import models

class RegisterView(generic.CreateView):
    """View for registration"""
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        # Generate verification token
        verification_token = get_random_string(50)
        user = form.save(commit=False)
        user.verification_token = verification_token
        user.save()

        # Send verification email
        subject = 'Verify your eBetStream account'
        message = f"""
        Thank you for registering on eBetStream!
        Please click on the following link to verify your email:
        {self.request.build_absolute_uri('/')}users/verify-email/?token={verification_token}
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        messages.success(self.request, 'Account created successfully! A verification email has been sent.')
        return super().form_valid(form)


class AdminRegisterView(generic.CreateView):
    """View for administrator registration"""
    form_class = AdminRegisterForm
    template_name = 'users/admin_register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        with db_transaction.atomic():
            # Create user with admin privileges
            user = form.save(commit=False)
            user.is_staff = True  # Access to admin interface
            user.email_verified = True  # No verification needed for admins
            user.save()
            
            # Record activity
            UserActivity.objects.create(
                user=user,
                activity_type='admin_registration',
                details=f"Registration as administrator"
            )
            
            messages.success(self.request, 'Administrator account created successfully! You can now log in.')
            return super().form_valid(form)


class LoginView(generic.FormView):
    """View for login"""
    form_class = UserLoginForm
    template_name = 'users/login.html'
    success_url = reverse_lazy('core:home')

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        
        # Record activity
        # Make sure user is a User instance
        from .models import User
        if isinstance(user, User):
            UserActivity.objects.create(
                user=user,
                activity_type='login',
                details=f"Login from {self.request.META.get('REMOTE_ADDR')}"
            )
        
        messages.success(self.request, f'Welcome {user.username}!')
        return super().form_valid(form)


class LogoutView(generic.View):
    """View for logout"""
    def get(self, request):
        # Record activity before logging out
        if request.user.is_authenticated:
            # Get user directly from database to avoid SimpleLazyObject
            from .models import User
            try:
                user = User.objects.get(pk=request.user.pk)
                UserActivity.objects.create(
                    user=user,
                    activity_type='logout',
                    details=f"Logout from {request.META.get('REMOTE_ADDR')}"
                )
            except User.DoesNotExist:
                pass
        
        logout(request)
        messages.info(request, 'You have been successfully logged out.')
        return redirect('core:home')


class ProfileView(generic.UpdateView):
    """View for user profile"""
    model = User
    form_class = UserUpdateForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        # Explicit form save with commit=True to ensure data is saved
        self.object = form.save(commit=True)
        # Force save form fields
        form.save_m2m()  # To save many-to-many relations if present
        # Refresh object from database
        self.object.refresh_from_db()
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


class ProfileDetailView(generic.DetailView):
    model = User
    template_name = 'users/profile_detail.html'
    context_object_name = 'user'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to access your profile.')
            return redirect('users:login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self, queryset=None):
        # Authentication check is already handled in dispatch
        # Get user directly from database to avoid SimpleLazyObject
        from .models import User
        try:
            # Get a complete User instance from the logged-in user's ID
            return User.objects.get(pk=self.request.user.pk)
        except User.DoesNotExist:
            # In case of error, redirect to login page
            messages.error(self.request, 'User not found. Please log in again.')
            return None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get user's transactions
        context['transactions'] = Transaction.objects.filter(user=self.object).order_by('-timestamp')
        
        # Get user directly from database
        from .models import User
        try:
            user = User.objects.get(pk=self.object.pk)
            # Add Ktap balance to context for display
            context['user_balance'] = user.kapanga_balance if user.kapanga_balance is not None else 0
            
            # Debug line
            print(f"Debug - Ktap balance in view: {context['user_balance']}")
        except User.DoesNotExist:
            context['user_balance'] = 0
        
        return context

class ProfileUpdateView(generic.UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'users/profile_form.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        # Explicit form save with commit=True to ensure data is saved
        self.object = form.save(commit=True)
        # Refresh object from database to ensure we have up-to-date data
        self.object.refresh_from_db()
        # Record user activity
        # Get user directly from database to avoid SimpleLazyObject
        from .models import User
        try:
            db_user = User.objects.get(pk=self.object.pk)
            UserActivity.objects.create(
                user=db_user,
                activity_type='profile_update',
                details=f"Profile update"
            )
        except User.DoesNotExist:
            pass
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


class TransactionHistoryView(LoginRequiredMixin, generic.ListView):
    """Vue pour l'historique des transactions"""
    model = Transaction
    template_name = 'users/transaction_history.html'
    context_object_name = 'transactions'
    paginate_by = 10

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-timestamp')


class DepositView(generic.FormView):
    """View for deposits"""
    form_class = DepositForm
    template_name = 'users/deposit.html'
    success_url = reverse_lazy('users:transaction_history')

    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        payment_method = form.cleaned_data['payment_method']

        with db_transaction.atomic():
            # Create transaction with 'pending' status
            transaction = Transaction.objects.create(
                user=self.request.user,
                amount=amount,
                transaction_type='deposit',
                status='pending',
                description=f"Deposit via {payment_method}",
                payment_method=payment_method  # Add payment_method
            )

            # Process transaction to update balance
            transaction.process_transaction()

            # Record activity
            UserActivity.objects.create(
                user=self.request.user,
                activity_type='deposit',
                details=f"Deposit of {amount} Ktap via {payment_method}"
            )

        messages.success(self.request, f'Deposit of {amount} Ktap completed successfully!')
        return super().form_valid(form)


class WithdrawalView(generic.FormView):
    """View for withdrawals"""
    form_class = WithdrawalForm
    template_name = 'users/withdrawal.html'
    success_url = reverse_lazy('users:transaction_history')

    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        payment_method = form.cleaned_data['payment_method']
        
        # Check if user has sufficient funds (using kapanga_balance)
        user_balance = self.request.user.kapanga_balance if self.request.user.kapanga_balance is not None else 0
        if user_balance < amount:
            messages.error(self.request, 'Insufficient Ktap balance to perform this withdrawal.')
            return self.form_invalid(form)
        
        # Create withdrawal transaction
        with db_transaction.atomic():
            transaction = Transaction.objects.create(
                user=self.request.user,
                amount=amount,
                transaction_type='withdrawal',
                description=f"Withdrawal via {dict(form.fields['payment_method'].choices)[payment_method]}",
                status='pending'
            )
            
            # Update user balance (deduct from kapanga_balance)
            self.request.user.kapanga_balance -= amount
            self.request.user.save()
        
        messages.success(self.request, f'Your withdrawal request of {amount} has been submitted successfully. It will be processed in the shortest possible time.')
        return super().form_valid(form)


class DepositRequestView(generic.CreateView):
    """View for deposit requests"""
    model = DepositRequest
    form_class = DepositRequestForm
    template_name = 'users/deposit_request.html'
    success_url = reverse_lazy('users:profile')
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to make a deposit request.')
            return redirect('users:login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get active payment methods
        context['payment_methods'] = PaymentMethod.objects.filter(is_active=True)
        
        # Add min and max amounts for display in template
        if context['payment_methods'].exists():
            context['min_amount'] = min([method.min_amount for method in context['payment_methods']])
            context['max_amount'] = max([method.max_amount for method in context['payment_methods']])
        else:
            context['min_amount'] = 5
            context['max_amount'] = 1000
            
        return context
    
    def form_valid(self, form):
        # Get user directly from database to avoid SimpleLazyObject
        from .models import User
        try:
            user = User.objects.get(pk=self.request.user.pk)
            deposit_request = form.save(commit=False)
            deposit_request.user = user
            deposit_request.save()

            # Record activity
            UserActivity.objects.create(
                user=user,
                activity_type='deposit_request',
                details=f"Deposit request of {deposit_request.amount} Ktap via {deposit_request.payment_method}"
            )

            messages.success(self.request, 'Deposit request submitted successfully!')
            return super().form_valid(form)
        except User.DoesNotExist:
            messages.error(self.request, 'User not found. Please log in again.')
            return redirect('users:login')


def verify_email(request):
    token = request.GET.get('token')
    if token:
        try:
            user = User.objects.get(verification_token=token)
            user.email_verified = True
            user.verification_token = None
            user.save()
            messages.success(request, 'Email verified successfully! You can now log in.')
        except User.DoesNotExist:
            messages.error(request, 'Invalid verification token.')
    else:
        messages.error(request, 'No verification token provided.')
    return redirect('users:login')


class PasswordChangeView(AuthPasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('users:password_change_done')

    def form_valid(self, form):
        messages.success(self.request, 'Password changed successfully!')
        return super().form_valid(form)

class PasswordResetView(AuthPasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')

class PasswordResetDoneView(AuthPasswordResetDoneView):
    template_name = 'users/password_reset_done.html'

class PasswordResetConfirmView(AuthPasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')

class PasswordResetCompleteView(AuthPasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'

class RequestWithdrawalView(LoginRequiredMixin, generic.CreateView):
    model = WithdrawalRequest
    form_class = WithdrawalRequestForm
    template_name = 'users/request_withdrawal.html'
    success_url = reverse_lazy('users:withdrawal_history')

    def form_valid(self, form):
        # Get user directly from database
        from .models import User
        try:
            user = User.objects.get(pk=self.request.user.pk)
            withdrawal_request = form.save(commit=False)
            withdrawal_request.user = user
            withdrawal_request.save()

            # Record activity
            UserActivity.objects.create(
                user=user,
                activity_type='withdrawal_request',
                details=f"Withdrawal request of {withdrawal_request.amount} Ktap via {withdrawal_request.payment_method}"
            )

            messages.success(self.request, 'Withdrawal request submitted successfully!')
            return super().form_valid(form)
        except User.DoesNotExist:
            messages.error(self.request, 'User not found. Please log in again.')
            return redirect('users:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment_methods'] = PaymentMethod.objects.filter(is_active=True)
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = {'user': self.request.user}
        return kwargs

class WithdrawalHistoryView(LoginRequiredMixin, generic.ListView):
    model = WithdrawalRequest
    template_name = 'users/withdrawal_history.html'
    context_object_name = 'withdrawal_requests'
    paginate_by = 10

    def get_queryset(self):
        return WithdrawalRequest.objects.filter(user=self.request.user).order_by('-created_at')

class WithdrawalRequestDetailView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    model = WithdrawalRequest
    template_name = 'users/withdrawal_request_detail.html'
    context_object_name = 'withdrawal_request'

    def test_func(self):
        withdrawal_request = self.get_object()
        return withdrawal_request.user == self.request.user

    def post(self, request, *args, **kwargs):
        withdrawal_request = self.get_object()
        action = request.POST.get('action')

        if action == 'cancel' and withdrawal_request.status == 'pending':
            withdrawal_request.status = 'cancelled'
            withdrawal_request.save()

            # Record activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='withdrawal_cancellation',
                details=f"Cancelled withdrawal request of {withdrawal_request.amount} Ktap"
            )

            messages.success(request, 'Withdrawal request cancelled successfully!')
        else:
            messages.error(request, 'Invalid action or withdrawal request cannot be cancelled.')

        return redirect('users:withdrawal_history')

class GameOrganizationRequestView(LoginRequiredMixin, generic.CreateView):
    """View for game organization request"""
    model = GameOrganizationRequest
    form_class = GameOrganizationRequestForm
    template_name = 'users/game_organization_request.html'
    success_url = reverse_lazy('users:profile') # Redirect to profile after success

    def form_valid(self, form):
        game_request = form.save(commit=False)
        game_request.user = self.request.user
        game_request.save()

        # Record activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='game_organization_request',
            details=f"Game organization request: {game_request.game_name}"
        )

        messages.success(self.request, 'Game organization request submitted successfully!')
        return super().form_valid(form)

class PromoCodeCreateView(LoginRequiredMixin, generic.CreateView):
    """Vue pour créer un code promo"""
    model = PromoCode
    template_name = 'users/promo_code_create.html'
    success_url = reverse_lazy('users:promo_code_list')
    fields = ['max_uses']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Code promo créé avec succès!')
        return super().form_valid(form)

class PromoCodeListView(LoginRequiredMixin, generic.ListView):
    """Vue pour lister les codes promo de l'utilisateur"""
    model = PromoCode
    template_name = 'users/promo_code_list.html'
    context_object_name = 'promo_codes'

    def get_queryset(self):
        return PromoCode.objects.filter(owner=self.request.user).order_by('-created_at')

class PromoCodeDetailView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    """Vue pour afficher les détails d'un code promo"""
    model = PromoCode
    template_name = 'users/promo_code_detail.html'
    context_object_name = 'promo_code'

    def test_func(self):
        promo_code = self.get_object()
        return promo_code.owner == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usages'] = self.object.usages.all().order_by('-created_at')
        return context

class PromoCodeUsageView(LoginRequiredMixin, generic.CreateView):
    """Vue pour utiliser un code promo lors d'un dépôt"""
    model = PromoCodeUsage
    template_name = 'users/promo_code_use.html'
    success_url = reverse_lazy('users:transaction_history')
    fields = ['promo_code']

    def form_valid(self, form):
        promo_code = form.cleaned_data['promo_code']
        
        # Vérifier si le code est valide
        if not promo_code.can_be_used():
            messages.error(self.request, 'Ce code promo n\'est plus valide.')
            return self.form_invalid(form)
        
        # Vérifier si l'utilisateur a déjà utilisé un code promo
        if PromoCodeUsage.objects.filter(user=self.request.user).exists():
            messages.error(self.request, 'Vous avez déjà utilisé un code promo.')
            return self.form_invalid(form)
        
        # Créer l'utilisation du code promo
        usage = form.save(commit=False)
        usage.user = self.request.user
        
        # Appliquer les bonus
        usage.apply_bonus()
        
        messages.success(self.request, 'Code promo utilisé avec succès! Les bonus ont été appliqués.')
        return super().form_valid(form)

@login_required
def vip_dashboard(request):
    user = request.user
    if not user.is_vip:
        return redirect('users:devenir_vip')
    solde_ktap = KtapToken.objects.filter(user=user, statut='disponible').aggregate(models.Sum('amount'))['amount__sum'] or 0
    ventes = VipSale.objects.filter(seller=user, statut='en_attente')
    bonus = VipBonus.objects.filter(user=user).order_by('-date')[:10]
    points = FidelityPoint.objects.filter(user=user).aggregate(models.Sum('points'))['points__sum'] or 0
    invitations = user.filleuls.all()
    context = {
        'solde_ktap': solde_ktap,
        'ventes': ventes,
        'bonus': bonus,
        'points': points,
        'invitations': invitations,
    }
    return render(request, 'users/vip/dashboard.html', context)

@login_required
def vip_market(request):
    user = request.user
    if not user.is_vip:
        return redirect('users:devenir_vip')
    ventes = VipSale.objects.filter(statut='en_attente').exclude(seller=user)
    if request.method == 'POST':
        if 'vente_id' in request.POST:
            # Achat d'une vente
            try:
                vente = VipSale.objects.select_for_update().get(id=request.POST['vente_id'], statut='en_attente')
                if vente.seller == user:
                    messages.error(request, "Vous ne pouvez pas acheter votre propre vente.")
                else:
                    # Vérifier le solde de l'acheteur
                    if user.kapanga_balance >= vente.amount * vente.price_per_token:
                        # Décrémenter le solde de l'acheteur
                        user.kapanga_balance -= vente.amount * vente.price_per_token
                        user.save()
                        # Créditer le vendeur
                        vente.seller.kapanga_balance += vente.amount * vente.price_per_token
                        vente.seller.save()
                        # Transférer les KTAP (optionnel : créer un KtapToken pour l'acheteur)
                        KtapToken.objects.create(user=user, amount=vente.amount, type='achat', statut='disponible')
                        vente.statut = 'vendu'
                        vente.save()
                        messages.success(request, f"Achat de {vente.amount} KTAP réussi !")
                    else:
                        messages.error(request, "Solde insuffisant pour cet achat.")
            except VipSale.DoesNotExist:
                messages.error(request, "Vente non disponible.")
            return redirect('users:vip_market')
        else:
            # Création d'une vente
            amount = int(request.POST.get('amount', 0))
            price = float(request.POST.get('price', 0))
            if amount > 0 and price > 0:
                VipSale.objects.create(seller=user, amount=amount, price_per_token=price)
                messages.success(request, "Vente créée avec succès.")
                return redirect('users:vip_market')
    return render(request, 'users/vip/market.html', {'ventes': ventes})

@login_required
def mes_evenements_vip(request):
    user = request.user
    if not user.is_vip:
        return redirect('users:devenir_vip')
    evenements = VipEvent.objects.filter(access_type__in=['vip_only', 'public']).order_by('-date')
    return render(request, 'users/vip/evenements.html', {'evenements': evenements})

@login_required
def mes_points_fidelite(request):
    user = request.user
    if not user.is_vip:
        return redirect('users:devenir_vip')
    points = FidelityPoint.objects.filter(user=user).order_by('-date')
    total = points.aggregate(models.Sum('points'))['points__sum'] or 0
    return render(request, 'users/vip/points.html', {'points': points, 'total': total})

def devenir_vip(request):
    user = request.user if request.user.is_authenticated else None
    demande = None
    if user:
        demande = VIPRequest.objects.filter(user=user).order_by('-date').first()
        if request.method == 'POST' and not user.is_vip:
            if not demande or demande.statut != 'en_attente':
                VIPRequest.objects.create(user=user)
                messages.success(request, "Votre demande VIP a été envoyée et sera traitée par l'administrateur.")
                return redirect('users:devenir_vip')
    return render(request, 'users/vip/devenir_vip.html', {'user': user, 'demande': demande})
