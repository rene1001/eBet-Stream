from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils.html import format_html
from django.urls import reverse
from .models import User, Transaction, PaymentMethod, DepositRequest, UserActivity, WithdrawalRequest, GameOrganizationRequest, PromoCode, PromoCodeUsage, KtapToken, VipSale, VipEvent, FidelityPoint, VipBonus, VIPRequest

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'balance', 'kapanga_balance', 'email_verified', 'is_active', 'is_vip', 'vip_since', 'vip_points', 'parrain', 'total_bonus')
    list_filter = ('is_active', 'email_verified', 'is_staff', 'is_superuser', 'is_vip')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login', 'uuid')
    fieldsets = (
        ('Personal Information', {'fields': ('username', 'email', 'first_name', 'last_name', 'profile_picture')}),
        ('Ktap Balance', {'fields': ('kapanga_balance',)}),
        ('Status', {'fields': ('is_active', 'email_verified', 'verification_token')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
        ('VIP Information', {'fields': ('is_vip', 'vip_since', 'vip_points', 'parrain', 'total_bonus')}),
    )

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'transaction_type', 'status', 'payment_method', 'timestamp')
    list_filter = ('transaction_type', 'status', 'payment_method', 'timestamp')
    search_fields = ('user__username', 'user__email', 'description', 'transaction_id')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'payment_method')

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'min_amount', 'max_amount', 'fee_percentage', 'processing_time')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    list_editable = ('is_active', 'min_amount', 'max_amount', 'fee_percentage')
    fieldsets = (
        ('Informations de base', {'fields': ('name', 'description', 'logo', 'is_active')}),
        ('Limites et frais', {'fields': ('min_amount', 'max_amount', 'fee_percentage', 'processing_time')}),
    )

@admin.register(DepositRequest)
class DepositRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_method', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('user__username', 'user__email', 'transaction_id')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 50
    
    actions = ['approve_deposits', 'reject_deposits']
    
    def approve_deposits(self, request, queryset):
        for deposit in queryset.filter(status='pending'):
            deposit.approve()
        self.message_user(request, f"{queryset.filter(status='approved').count()} deposits have been approved.")
    approve_deposits.short_description = "Approve selected deposits"
    
    def reject_deposits(self, request, queryset):
        for deposit in queryset.filter(status='pending'):
            deposit.reject()
        self.message_user(request, f"{queryset.filter(status='rejected').count()} deposits have been rejected.")
    reject_deposits.short_description = "Reject selected deposits"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'payment_method')

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'timestamp', 'details')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('user__username', 'user__email', 'details')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
    list_per_page = 50
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
        
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'approve/<int:withdrawal_id>/',
                self.admin_site.admin_view(self.approve_withdrawal_view),
                name='approve_withdrawal',
            ),
            path(
                'reject/<int:withdrawal_id>/',
                self.admin_site.admin_view(self.reject_withdrawal_view),
                name='reject_withdrawal',
            ),
        ]
        return custom_urls + urls
        
    def approve_withdrawal_view(self, request, withdrawal_id):
        withdrawal = get_object_or_404(WithdrawalRequest, id=withdrawal_id)
        if withdrawal.status == 'pending':
            success = withdrawal.approve()
            if success:
                messages.success(request, f"Withdrawal request of {withdrawal.amount} Ktap for {withdrawal.user.username} has been approved.")
            else:
                messages.error(request, "Error while approving the withdrawal request.")
        return redirect('admin:users_withdrawalrequest_changelist')
        
    def reject_withdrawal_view(self, request, withdrawal_id):
        withdrawal = get_object_or_404(WithdrawalRequest, id=withdrawal_id)
        if withdrawal.status == 'pending':
            success = withdrawal.reject()
            if success:
                messages.success(request, f"Withdrawal request of {withdrawal.amount} Ktap for {withdrawal.user.username} has been rejected.")
            else:
                messages.error(request, "Error while rejecting the withdrawal request.")
        return redirect('admin:users_withdrawalrequest_changelist')

@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_method', 'status', 'created_at', 'updated_at', 'payment_references', 'actions_buttons')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('user__username', 'user__email', 'paypal_email', 'crypto_address')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'payment_references')
    list_per_page = 50
    
    actions = ['approve_withdrawal_requests', 'reject_withdrawal_requests']

    fieldsets = (
        (None, {'fields': ('user', 'amount', 'payment_method', 'status', 'admin_notes', 'paypal_email', 'crypto_address')}),
        ('Dates', {'fields': ('created_at', 'updated_at', 'payment_references')}),
    )
    
    def payment_references(self, obj):
        """Display payment references based on the chosen method"""
        if obj.payment_method == 'paypal':
            return format_html(
                "<strong>PayPal Email:</strong> <a href='mailto:{}'>{}</a>",
                obj.paypal_email or 'Not specified',
                obj.paypal_email or 'Not specified'
            )
        elif obj.payment_method == 'crypto':
            return format_html(
                "<strong>Crypto Address:</strong> <span class='text-monospace'>{}</span>",
                obj.crypto_address or 'Not specified'
            )
        else:
            return "No payment reference available"
    payment_references.short_description = "Payment References"
    payment_references.allow_tags = True
    
    def actions_buttons(self, obj):
        """Add action buttons to approve/reject directly from the list"""
        if obj.status == 'pending':
            return format_html(
                '<a class="button" href="{}" style="background-color: #28a745; color: white; margin-right: 5px;">Approve</a>'
                '<a class="button" href="{}" style="background-color: #dc3545; color: white;">Reject</a>',
                reverse('admin:approve_withdrawal', args=[obj.pk]),
                reverse('admin:reject_withdrawal', args=[obj.pk])
            )
        elif obj.status == 'approved':
            return format_html('<span style="color: green;">Approved</span>')
        else:
            return format_html('<span style="color: red;">Rejected</span>')
    actions_buttons.short_description = "Actions"
    actions_buttons.allow_tags = True
    
    def approve_withdrawal_requests(self, request, queryset):
        for withdrawal_request in queryset.filter(status='pending'):
            withdrawal_request.approve()
        self.message_user(request, f"{queryset.filter(status='approved').count()} withdrawal requests have been approved.")
    approve_withdrawal_requests.short_description = "Approve selected withdrawal requests"
    
    def reject_withdrawal_requests(self, request, queryset):
        for withdrawal_request in queryset.filter(status='pending'):
            withdrawal_request.status = 'rejected'
            withdrawal_request.save()
        self.message_user(request, f"{queryset.filter(status='rejected').count()} withdrawal requests have been rejected.")
    reject_withdrawal_requests.short_description = "Reject selected withdrawal requests"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
        
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'approve/<int:withdrawal_id>/',
                self.admin_site.admin_view(self.approve_withdrawal_view),
                name='approve_withdrawal',
            ),
            path(
                'reject/<int:withdrawal_id>/',
                self.admin_site.admin_view(self.reject_withdrawal_view),
                name='reject_withdrawal',
            ),
        ]
        return custom_urls + urls
        
    def approve_withdrawal_view(self, request, withdrawal_id):
        withdrawal = get_object_or_404(WithdrawalRequest, id=withdrawal_id)
        if withdrawal.status == 'pending':
            success = withdrawal.approve()
            if success:
                messages.success(request, f"Withdrawal request of {withdrawal.amount} Ktap for {withdrawal.user.username} has been approved.")
            else:
                messages.error(request, "Error while approving the withdrawal request.")
        return redirect('admin:users_withdrawalrequest_changelist')
        
    def reject_withdrawal_view(self, request, withdrawal_id):
        withdrawal = get_object_or_404(WithdrawalRequest, id=withdrawal_id)
        if withdrawal.status == 'pending':
            success = withdrawal.reject()
            if success:
                messages.success(request, f"Withdrawal request of {withdrawal.amount} Ktap for {withdrawal.user.username} has been rejected.")
            else:
                messages.error(request, "Error while rejecting the withdrawal request.")
        return redirect('admin:users_withdrawalrequest_changelist')

@admin.register(GameOrganizationRequest)
class GameOrganizationRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'game_name', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'game_name', 'description')
    readonly_fields = ('user', 'created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('user', 'game_name', 'description', 'status', 'admin_notes')}),
        ('Dates', {'fields': ('created_at', 'updated_at')}),
    )
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f"{queryset.count()} requests have been approved.")
    approve_requests.short_description = "Approve selected requests"
    
    def reject_requests(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} requests have been rejected.")
    reject_requests.short_description = "Reject selected requests"

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'owner', 'created_at', 'is_active', 'usage_count', 'max_uses')
    list_filter = ('is_active', 'created_at')
    search_fields = ('code', 'owner__username')
    readonly_fields = ('code', 'created_at', 'usage_count')
    fieldsets = (
        ('Informations de base', {
            'fields': ('code', 'owner', 'created_at')
        }),
        ('Statut', {
            'fields': ('is_active', 'usage_count', 'max_uses')
        }),
    )

@admin.register(PromoCodeUsage)
class PromoCodeUsageAdmin(admin.ModelAdmin):
    list_display = ('promo_code', 'user', 'deposit', 'created_at', 'bonus_amount')
    list_filter = ('created_at',)
    search_fields = ('promo_code__code', 'user__username')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Informations de base', {
            'fields': ('promo_code', 'user', 'deposit', 'created_at')
        }),
        ('Bonus', {
            'fields': ('bonus_amount',)
        }),
    )

@admin.register(KtapToken)
class KtapTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'type', 'statut', 'created_at')
    list_filter = ('type', 'statut')
    search_fields = ('user__username',)

@admin.register(VipSale)
class VipSaleAdmin(admin.ModelAdmin):
    list_display = ('seller', 'amount', 'price_per_token', 'statut', 'created_at')
    list_filter = ('statut',)
    search_fields = ('seller__username',)

@admin.register(VipEvent)
class VipEventAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type', 'date', 'access_type', 'created_at')
    list_filter = ('type', 'access_type')
    search_fields = ('nom',)

@admin.register(FidelityPoint)
class FidelityPointAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'type', 'date')
    list_filter = ('type',)
    search_fields = ('user__username',)

@admin.register(VipBonus)
class VipBonusAdmin(admin.ModelAdmin):
    list_display = ('user', 'bonus_type', 'montant', 'date')
    list_filter = ('bonus_type',)
    search_fields = ('user__username',)

@admin.register(VIPRequest)
class VIPRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'statut', 'date', 'commentaire_admin')
    list_filter = ('statut',)
    search_fields = ('user__username',)
    actions = ['accepter_demande', 'rejeter_demande']

    def accepter_demande(self, request, queryset):
        for demande in queryset.filter(statut='en_attente'):
            demande.statut = 'acceptee'
            demande.save()
            user = demande.user
            user.is_vip = True
            user.vip_since = demande.date
            user.save()
        self.message_user(request, "Demande(s) acceptée(s) et utilisateur(s) promu(s) VIP.")
    accepter_demande.short_description = "Accepter la demande et promouvoir VIP"

    def rejeter_demande(self, request, queryset):
        for demande in queryset.filter(statut='en_attente'):
            demande.statut = 'rejetee'
            demande.commentaire_admin = "Rejeté par l'admin."
            demande.save()
        self.message_user(request, "Demande(s) rejetée(s).")
    rejeter_demande.short_description = "Rejeter la demande VIP"
