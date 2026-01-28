"""
URL configuration for bank_website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from accounts import views
from accounts.views import (
    login_success, 
    account_list, 
    customer_dashboard, 
    signup_view, 
    transaction_receipt, 
    deposit_money,    # <--- Make sure these are here
    withdraw_money,   # <--- 
    transfer_money, 
    identity_verification, 
    approve_account,
    delete_account
    )

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('boss/',views.account_list,name='boss_portal'),
    path('accounts/', include('django.contrib.auth.urls')),# NEW: Built-in login/logout
    
    path('signup/', signup_view, name='signup'),  # NEW: User registration
    path('', account_list, name='account_list'),  # Home page showing account list
    path('dashboard/', customer_dashboard, name='customer_dashboard'),  # Customer dashboard
    path('receipt/<uuid:ref_id>/',transaction_receipt,name='transaction_receipt'),
   # path('delete_account/<int:pk>/', delete_account, name='delete_account'),
    path('deposit/', deposit_money, name='deposit_money'),
    path('withdraw/', withdraw_money, name='withdraw_money'),
    path('transfer_money/' ,transfer_money, name='transfer_money'),
    path('verify/', views.identity_verification, name='verify_identity'),
    path('approve/<int:account_id>/', views.approve_account, name='approve_account'),
    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)