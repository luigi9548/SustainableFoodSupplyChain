from models.model_base import Model
from colorama import Fore, Style, init
from db.db_operations import DatabaseOperations

class Licences(Model):
    """
    This class defines the Licence model, which associates a licence ID with a specific account type,  
    extending the functionality provided by the Model class.
    """

    def __init__(self, id, type, licence_number, db):
        """
        Initializes a new instance of the Licence class, associating a licence ID with an account type.

        Parameters:
        - id: Unique identifier for the licence record  
        - type: The category of licence ('FARMER', 'CARRIER', 'SELLER', 'PRODUCER', 'CERTIFIER')  
        - licence_number: A unique identifier assigned to the licence  
        """
        super().__init__()
        self.id = id
        self.type = type
        self.licence_number = licence_number
        self.db = db

    # Getter method for each attribute
    def get_id(self):
        return self.id

    def get_type(self):
        return self.type

    def get_licence_number(self):
        return self.licence_number

    def save(self):
        """
        Saves a new or updates an existing Licences record in the database.
        Implements SQL queries to insert or update licences based on the presence of an ID.
        """
        if self.id is None:
            # Insert new licences record
            result = self.db.register_licences(self.type, self.licence_number)
            if result == 0:
                self.id = self.cur.lastrowid
        else:
            # Update existing licences record
            result = self.db.update_licences(self.id, self.type,
                                             self.licence_number)
        if result == 0:
            print(Fore.GREEN + 'Information saved correctly!\n' + Style.RESET_ALL)
        else:
            print(Fore.RED + 'Error saving information!\n' + Style.RESET_ALL)
        return result

    def delete(self):
        """
        Deletes a Lincences record from the database based on its ID.
        """
        if self.id is not None:
            result = self.db.delete_licences(self.id)
            if result == 0:
                print(Fore.GREEN + 'Information deleted correctly!\n' +
                      Style.RESET_ALL)
            else:
                print(Fore.RED + 'Error deleting information!\n' +
                      Style.RESET_ALL)
            return result
        else:
            return -1