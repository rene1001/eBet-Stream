from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('register/admin/', views.AdminRegisterView.as_view(), name='admin_register'),
    path('profile/', views.ProfileDetailView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('deposit-request/', views.DepositRequestView.as_view(), name='deposit_request'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password/reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/complete/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('request_withdrawal/', views.RequestWithdrawalView.as_view(), name='request_withdrawal'),
    path('withdrawal_history/', views.WithdrawalHistoryView.as_view(), name='withdrawal_history'),
    path('withdrawal-request/<int:pk>/', views.WithdrawalRequestDetailView.as_view(), name='withdrawal_request_detail'),
    path('game-organization-request/', views.GameOrganizationRequestView.as_view(), name='game_organization_request'),
    path('transaction-history/', views.TransactionHistoryView.as_view(), name='transaction_history'),
    
    # URLs pour les codes promo
    path('promo-codes/', views.PromoCodeListView.as_view(), name='promo_code_list'),
    path('promo-codes/create/', views.PromoCodeCreateView.as_view(), name='promo_code_create'),
    path('promo-codes/<int:pk>/', views.PromoCodeDetailView.as_view(), name='promo_code_detail'),
    path('promo-codes/use/', views.PromoCodeUsageView.as_view(), name='promo_code_use'),
    path('vip/', views.vip_dashboard, name='vip_dashboard'),
    path('vip/market/', views.vip_market, name='vip_market'),
    path('vip/evenements/', views.mes_evenements_vip, name='mes_evenements_vip'),
    path('vip/points/', views.mes_points_fidelite, name='mes_points_fidelite'),
    path('devenir-vip/', views.devenir_vip, name='devenir_vip'),
]