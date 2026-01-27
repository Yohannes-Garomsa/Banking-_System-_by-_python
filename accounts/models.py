from django.db import models

# Create your models here.
class Account(models.Model):
    owner=models.CharField(max_length=100)
    balance=models.DecimalField(max_digits=15,decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.owner}-${self.balance}"