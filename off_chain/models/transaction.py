from models.model_base import Model
from colorama import Fore, Style

class Transaction(Model):
    """
    This class defines the Transaction model, which stores information about different types of transactions,  
    extending the functionality provided by the Model class.
    """

    def __init__(self, id, username_from, username_to, amount, type, tx_hash, timestamp):
        """
        Initializes a new instance of the Transaction class, representing a specific action or investment.

        Parameters:
        - id: Unique identifier for the transaction record
        - username_from: Username of the sender
        - username_to: Username of the recipient
        - amount: Amount of the transaction
        - type: Type of transaction (e.g., MINT, BURN, TRANSFER)
        - tx_hash: Transaction hash
        - timestamp: Timestamp of the transaction

        """
        super().__init__()
        self.id = id
        self.username_from = username_from
        self.username_to = username_to
        self.amount = amount
        self.type = type
        self.tx_hash = tx_hash
        self.timestamp = timestamp

    # Getter methods for each attribute
    def get_id(self):
        return self.id

    def get_username_from(self):
        return self.username_from

    def get_username_to(self):
        return self.username_to

    def get_amount(self):
        return self.amount

    def get_type(self):
        return self.type

    def get_tx_hash(self):
        return self.tx_hash

    def get_timestamp(self):
        return self.timestamp

    def delete(self):
        """
        Deletes an Account record from the database based on its ID.
        """
      
        if self.id is not None:
            result = db.delete_account(self.id)
            if result == 0:
                print(Fore.GREEN + 'Account deleted successfully!\n' + Style.RESET_ALL)
            else:
                print(Fore.RED + 'Error deleting account!\n' + Style.RESET_ALL)
            return result
        else:
            return -1 
