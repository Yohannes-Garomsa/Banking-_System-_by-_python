from django.db import models
from django.contrib.auth.models import User # Built-in User system

# Create your models here.
class Account(models.Model):
    # Link to a real User login
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    owner = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.owner}'s Account"
    
class Transaction(models.Model):
    sender=models.CharField(max_length=100)
    receiver=models.CharField(max_length=100)
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    timestamp=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.sender} sent ${self.amount} to {self.receiver} on {self.timestamp}"