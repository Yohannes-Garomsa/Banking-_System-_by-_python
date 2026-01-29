import random
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

class Account(models.Model):
    ACCOUNT_TYPES = [('savings', 'Savings'), ('checking', 'Checking')]
    
    OCCUPATION_CHOICES = [
        ('student', 'Student'),
        ('employee', 'Employee'),
        ('business', 'Business/Self-Employed'),
        ('other', 'Other'),
    ]

    # Core Relationship
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='account')
    
    # Banking Details
    account_number = models.CharField(max_length=12, unique=True, blank=True)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES, default='savings')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    # --- NEW SECURITY FEATURE ---
    # is_active handles general status, is_frozen specifically blocks transactions
    is_active = models.BooleanField(default=True) 
    is_frozen = models.BooleanField(default=False) 

    # KYC & Identity Verification
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    occupation = models.CharField(max_length=20, choices=OCCUPATION_CHOICES, null=True, blank=True)
    id_card_photo = models.ImageField(upload_to='identity/ids/', blank=True, null=True)
    selfie_photo = models.ImageField(upload_to='identity/selfies/', blank=True, null=True)
    
    is_verified = models.BooleanField(default=False)
    kyc_step = models.IntegerField(default=1) # Tracks step (1: Phone, 2: ID, 3: Face)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_account_number():
        """Generates a unique 10-digit bank account number"""
        return "".join([str(random.randint(0, 9)) for _ in range(10)])

    def __str__(self):
        return f"{self.user.username}'s Account ({self.account_number})"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('DEP', 'Deposit'),
        ('WDL', 'Withdrawal'),
        ('TRF', 'Transfer'),
    )

    ref_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sender = models.CharField(max_length=100)
    receiver = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tx_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES, default='TRF')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tx_type} - {self.amount} (Ref: {self.ref_id})"

class OnboardingApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    full_name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    kebele = models.CharField(max_length=100)
    national_id = models.CharField(max_length=50)
    job_position = models.CharField(max_length=100)
    age = models.IntegerField()
    phone = models.CharField(max_length=20)
    
    # Security Capture Status
    is_id_captured = models.BooleanField(default=False)
    is_face_captured = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.status}"

# Signal to auto-create Account when a User is registered
@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        # Check if account exists to prevent duplicates
        Account.objects.get_or_create(user=instance)