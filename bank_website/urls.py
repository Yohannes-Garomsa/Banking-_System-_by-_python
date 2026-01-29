from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from accounts import views  # Single clean import for all account logic

urlpatterns = [
    # --- System Admin (Django Built-in) ---
    path('admin/', admin.site.urls),
    
    # --- Geda Bank Boss Portal (Administrative Management) ---
    path('boss-portal/', views.boss_dashboard, name='boss_portal'),
    path('approve-kyc/<int:app_id>/', views.approve_kyc, name='approve_kyc'),
    path('delete_account/<int:pk>/', views.delete_account, name='delete_account'),
    
    # NEW FEATURE: Security Toggle for Freezing/Unfreezing accounts
    path('toggle-freeze/<int:pk>/', views.toggle_freeze, name='toggle_freeze'),
    
    # --- Authentication & Registration ---
    path('accounts/', include('django.contrib.auth.urls')), 
    path('signup/', views.signup_view, name='signup'),
    path('login-success/', views.login_success, name='login_success'), # Redirects Boss vs Customer
    
    # --- Customer Interface ---
    path('', TemplateView.as_view(template_name='registration/landing_page.html'), name='landing_page'),
    path('onboarding/', views.onboarding, name='onboarding'),
    path('submit-onboarding/', views.submit_onboarding, name='submit_onboarding'), # AJAX path
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('verify/', views.identity_verification, name='verify_identity'),
    
    # --- Banking Operations ---
    path('deposit/', views.deposit_money, name='deposit_money'),
    path('withdraw/', views.withdraw_money, name='withdraw_money'),
    path('transfer/', views.transfer_money, name='transfer_money'),
    path('receipt/<uuid:ref_id>/', views.transaction_receipt, name='transaction_receipt'),
]

# Serve media files (ID photos/Face captures)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)