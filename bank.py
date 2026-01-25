class bankAccount:
    def __init__(self,owner,balance=0):
        self.owner=owner
        self.balance=balance
        
    def deposite(self,amount):
        self.balance += amount
        print(f"Added {amount}. New balance is {self.balance}")
        
    def withdraw(self, amount):
        if amount <=self.balance:
            self.balance -=amount
            print(f"Withdrew {amount}. New balance is {self.balance}")
        else:
            print("Insufficient funds")
            
    def transfer(self, amount, to_account):
        if amount <=self.balance:
            self.balance-=amount
            to_account.deposite(amount)
            print(f"Transferred {amount} to {to_account.owner} from {self.owner}. New balance is {self.balance}")
        else:
            print("transfer failed! {self.owner} has insufficient funds.")
class SavingsAccount(bankAccount):
    def __init__(self, owner, balance,interest_rate):
        # 'super()' calls the __init__ of the Parent (BankAccount)
        # This handles the owner and balance for us!
        super().__init__(owner, balance)
        self.interest_rate = interest_rate
    def add_interest(self):
        interest = self.balance* self.interest_rate
        self.balance +=interest
        print(f"interest added ! New balance for {self.owner}: ${self.balance}")
    
    
    """Create a new Child class called BusinessAccount.

    It should inherit from BankAccount.

    It should have an attribute called transaction_fee = 2.

    Override the withdraw method: Every time a business withdraws money, it should subtract the amount PLUS the $2 fee.
    """
class BusinessAccount(bankAccount):
    def __init__(self, owner, balance=0):
        super().__init__(owner, balance)
        self.transaction_fee = 2

    def withdraw(self, amount):
        total_deduction =amount +self.transaction_fee
        
        
        if self.balance >= total_deduction:
            self.balance -= total_deduction
            print(f"Business withdrawal of ${amount} (including fee of ${self.transaction_fee}).")
            print(f"New balance is ${self.balance}")
        else:
           print(f"Insufficient funds to cover amount and ${self.transaction_fee} fee!")


class SmartAccount(bankAccount):
    def __init__(self, owner, balance):
        super().__init__(owner, balance)
        self.balance=balance
    def get_balance(self):
        return f"the current balance is ${self.balance}"
    
print("-----basic  account-----")
acc1= bankAccount("john",6000) 
acc2= bankAccount("meri",5000)

acc1.deposite(500)
acc1.withdraw(200)

acc1.transfer(500,acc2)
print(acc1.balance)
print(acc2.balance)

print("-----savings account-----")
savings_acc= SavingsAccount("Alice",10000,0.05)

# Using inherited methods
savings_acc.deposite(2000)
# Using unique child methods
savings_acc.add_interest()
    
print("-----business account-----")
business_acc= BusinessAccount("Bob's Burgers",15000)
business_acc.withdraw(1000)  # Should deduct $1002 including the fee
business_acc.withdraw(14999)  # Should print insufficient funds message
print("-----smart account-----")
my_acc=SmartAccount("Alice", 3000)  
print(my_acc.get_balance())  # Output: the current balance is $3000
my_acc.__balance =5000000
print(my_acc.get_balance())  # Output: the current balance is $3000
            