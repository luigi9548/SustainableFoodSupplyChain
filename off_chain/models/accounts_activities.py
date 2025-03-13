import re
from models.model_base import Model
from db.db_operations import DatabaseOperations
from colorama import Fore, Style, init

class Accounts_Activities(Model):
    """
    This class defines the Accounts_Activities model, which establishes a relationship between user accounts and 
    the activities they are associated with, extending the functionality provided by the Model class.
    """
    def __init__(self, account_id, activity_id, db):
        """
        Initializes a new instance of the Accounts_Activities class, linking a specific account to an activity.

        Parameters:
        - account_id: The unique identifier of the account  
        - activity_id: The unique identifier of the activity associated with the account  
        """
        super().__init__()
        self.account_id = account_id
        self.activity_id = activity_id
        self.db = db

    # Getter methods for each attribute
    def get_account_id(self):
        return self.account_id

    def get_activity_id(self):
        return self.activity_id

    def save(self):
        """
        Saves a new or updates an existing Credentials record in the database.
        Implements SQL queries to insert or update credentials based on the presence of an ID.
        """
        if self.id is None:
             # Insert new account_activities record
             result = self.db.register_account_activities(self.account_id, self.activity_id)
             if result == 0:
                self.id = self.cur.lastrowid # Update the ID with the last row inserted ID if new record
        else:
             # Update existing account_activities record
                self.db.update_account_activities(self.id, self.account_id, self.activity_id)
        if result == 0:
            print(Fore.GREEN + 'Information saved correctly!\n' + Style.RESET_ALL)
        else:
            print(Fore.RED + 'Error saving information!\n' + Style.RESET_ALL)
        return result

    def delete(self):
        """
        Deletes an existing account_activities record from the database.
        """
        if self.id is not None:
            result = self.db.delete_account_activities(self.id)
            if result == 0:
                print(Fore.GREEN + 'Information deleted correctly!\n' + Style.RESET_ALL)
            else:
                print(Fore.RED + 'Error deleting information!\n' + Style.RESET_ALL)
            return result
        else:
            return -1
        