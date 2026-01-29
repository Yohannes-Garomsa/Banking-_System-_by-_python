from django.contrib import admin
from.models import Account
from .models import OnboardingApplication

# Register your models here.
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display=('user','account_number','account_type','balance', 'is_active')
    
@admin.register(OnboardingApplication)
class OnboardingApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'account_number')
    actions = ['approve_application', 'reject_application']

    def approve_application(self, request, queryset):
        queryset.update(status='approved')
    approve_application.short_description = "Approve selected applications"