from django.db import models
from django.contrib.auth.models import User # Built-in User system
import uuid

# Create your models here.
class Account(models.Model):
    # Link to a real User login
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    owner = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.owner}'s Account"
    
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
    
