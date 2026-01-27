from account_repository import save_account, get_account, update_balance

class bankAccount:
    def __init__(self,owner,balance=0):
        self.owner=owner
        self.balance=balance
        
    def deposit(self,amount):
        self.balance += amount
        print(f"Added {amount}. New balance is {self.balance}")
        try:
            update_balance(self.owner, self.balance)
        except Exception:
            pass
        
    def withdraw(self, amount):
        if amount <=self.balance:
            self.balance -=amount
            print(f"Withdrew {amount}. New balance is {self.balance}")
            try:
                update_balance(self.owner, self.balance)
            except Exception:
                pass
        else:
            print("Insufficient funds")
            
    def transfer(self, amount, to_account):
        if amount <=self.balance:
            self.balance-=amount
            # call deposit on target account and persist both sides
            to_account.deposit(amount)
            print(f"Transferred {amount} to {to_account.owner} from {self.owner}. New balance is {self.balance}")
            try:
                update_balance(self.owner, self.balance)
            except Exception:
                pass
            try:
                update_balance(to_account.owner, to_account.balance)
            except Exception:
                pass
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
        try:
            update_balance(self.owner, self.balance)
        except Exception:
            pass
    
    
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
    
 
 
 
acc1 = bankAccount("John", 1000)
acc1.deposit(2000)

acc2 = SavingsAccount("Jane", 1500, 0.03)
acc2.add_interest()

# persist initial accounts: insert if not exists, otherwise update
for acc in (acc1, acc2):
    try:
        existing = get_account(acc.owner)
        if existing is None:
            save_account(acc.owner, acc.balance)
        else:
            update_balance(acc.owner, acc.balance)
    except Exception:
        # if DB not configured, ignore and continue
        pass