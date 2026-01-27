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
from accounts.views import (
    account_list, 
    delete_account ,
    customer_dashboard ,
    signup_view,
    transaction_receipt,
    deposit_money,
    withdraw_money)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),# NEW: Built-in login/logout
    
    path('signup/', signup_view, name='signup'),  # NEW: User registration
    path('', account_list, name='account_list'),  # Home page showing account list
    path('dashboard/', customer_dashboard, name='customer_dashboard'),  # Customer dashboard
    path('receipt/<uuid:ref_id>/',transaction_receipt,name='transaction_receipt'),
    path('delete_account/<int:pk>/', delete_account, name='delete_account'),
    path('deposit/', deposit_money, name='deposit_money'),
path('withdraw/', withdraw_money, name='withdraw_money'),
    
]