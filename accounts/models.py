from django.db import models
from django.contrib.auth.models import User # Built-in User system
import uuid
from django.db.models.signals import post_save

from django.dispatch import receiver

# Create your models here.
class Account(models.Model):
    # Link to a real User login
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    owner = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.owner}'s Account"
    is_verified =models.BooleanField(default=False)
    id_card_photo=models.ImageField(upload_to='verifications/ids/',null=True, blank=True)
    live_selfie=models.ImageField(upload_to='veifications/selfies/',null=True, blank=True)
    phone_number=models.CharField(max_length=15,unique=True,null=True,blank=True)
    
    def __str__(self):
        return f"{self.user.username}-{' ✅ verified' if self.is_verified else  '⏳ pending'}"
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
