from django.db import models

# Create your models here.
class Account(models.Model):
    owner=models.CharField(max_length=100)
    balance=models.DecimalField(max_digits=15,decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.owner}-${self.balance}"
class Transaction(models.Model):
    sender=models.CharField(max_length=100)
    receiver=models.CharField(max_length=100)
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    timestamp=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.sender} sent ${self.amount} to {self.receiver} on {self.timestamp}"