from django.db import models
from django.contrib.auth.models import User # Built-in User system
import uuid
from django.db.models.signals import post_save

from django.dispatch import receiver

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    owner = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Professional Verification Fields
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    
    # Image Storage
    id_card_photo = models.ImageField(upload_to='identity/ids/', blank=True, null=True)
    selfie_photo = models.ImageField(upload_to='identity/selfies/', blank=True, null=True)
    
    # Status Tracking
    is_verified = models.BooleanField(default=False)
    kyc_step = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.owner}'s Account - Status: {'Verified' if self.is_verified else 'Pending'}"
    
    OCCUPATION_CHOICES = [
        ('student', 'Student'),
        ('employee', 'Employee'),
        ('business', 'Business/Self-Employed'),
        ('other', 'Other'),
    ]
    occupation = models.CharField(max_length=20, choices=OCCUPATION_CHOICES, null=True, blank=True)
    kyc_step = models.IntegerField(default=1) # Track which step the user is on
class Transaction(models.Model):
      
      TRANSACTION_TYPES=(
        ('DEP','Deposit'),
        ('WDL','Withdrawal'),
        ('TRF','Transfer'),
      )
    
     #Add unique reference id for each transaction
      ref_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
      sender=models.CharField(max_length=100)
      receiver=models.CharField(max_length=100)
      amount=models.DecimalField(max_digits=10,decimal_places=2)
      tx_type=models.CharField(max_length=3,choices=TRANSACTION_TYPES,default='TRF')
      timestamp=models.DateTimeField(auto_now_add=True)
      def __str__(self):
          
        return f"{self.tx_type} -${self.ref_id} "
    
@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.get_or_create(user=instance)
