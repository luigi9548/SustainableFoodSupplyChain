from models.model_base import Model
from colorama import Fore, Style, init
# from db.db_operations import DatabaseOperations

class Accounts(Model):
    """
    This class defines the Account model, which stores user account details,  
    extending the functionality provided by the Model class.
    """

    def __init__(self, id, credential_id, type, name, licence_id, lastname, birthday, birth_place, residence, phone, mail):
        """
        Initializes a new instance of Account class with the provided account  details.

        Parameters:
        - id: Unique identifier for the account record
        - credential_id: User credentials id that is associated with this account
        - type: The type of account ('FARMER', 'CARRIER', 'SELLER', 'PRODUCER', 'CERTIFIER')
        - name: The first name of the account holder
        - licence_id: Licence id that is associated with this account
        - lastname: The last name of the account holder
        - birthday: The birth date of the account holder, stored as a string in the format 'YYYY-MM-DD' ????
        - birth_place: The place of birth of the account holder (optional)
        - residence: The address where the account holder resides (optional)
        - phone: The phone number of the account holder (optional)
        - mail: The email address of the account holder (optional)
        """
        super().__init__()
        self.id = id
        self.credential_id = credential_id
        self.type = type
        self.name = name
        self.licence_id = licence_id
        self.lastname = lastname
        self.birthday = birthday
        self.birth_place = birth_place
        self.residence = residence
        self.phone = phone
        self.mail = mail
      #  self.db = db

    # Getter methods for each attribute
    def get_id(self):
        return self.id

    def get_credential_id(self):
        return self.credential_id

    def get_type(self):
        return self.type

    def get_name(self):
        return self.name

    def get_licence_id(self):
        return self.licence_id

    def get_lastname(self):
        return self.lastname

    def get_birthday(self):
        return self.birthday

    def get_birth_place(self):
        return self.birth_place

    def get_residence(self):
        return self.residence

    def get_phone(self):
        return self.phone

    def get_mail(self):
        return self.mail

    # Setter methods for each attribute
    def set_id(self, id):
        self.id = id

    def set_credential_id(self, credential_id):
        self.credential_id = credential_id

    def set_type(self, type):
        self.type = type
    
    def set_name(self, name):
        self.name = name

    def set_licence_id(self, licence_id):
        self.licence_id = licence_id

    def set_lastname(self, lastname):
        self.lastname = lastname

    def set_birthday(self, birthday):
        self.birthday = birthday

    def set_birth_place(self, birth_place):
        self.birth_place = birth_place

    def set_residence(self, residence):
        self.residence = residence

    def set_phone(self, phone):
        self.phone = phone

    def set_mail(self, mail):
        self.mail = mail
      
    """def save(self):

        Saves a new or updates an existing Accounts record in the database.
        Implements SQL queries to insert or update credentials based on the presence of an ID.

        if self.id is None:
            # Inserts new accounts record into the database
            result = db.register_account(self.credential_id, self.type, self.name, self.lastname, self.birthday,
                                         self.birth_place, self.residence, self.phone, self.mail)
            if result == 0:
                self.id = self.cur.lastrowid
        else:
            # Updates existing accounts record in the database 
            result = db.update_account(self.credential_id, self.type, self.name, self.licence_id, self.lastname, self.birthday, 
                                        self.birth_place, self.residence, self.phone, self.mail, self.id)    
        if result == 0:
            print(Fore.GREEN + 'Information saved correctly!\n' + Style.RESET_ALL)
        else:
            print(Fore.RED + 'Error saving information!\n' + Style.RESET_ALL)
        
    def delete(self):

        Deletes an Account record from the database based on its ID.
      
        if self.id is not None:
            result = db.delete_account(self.id)
            if result == 0:
                print(Fore.GREEN + 'Account deleted successfully!\n' + Style.RESET_ALL)
            else:
                print(Fore.RED + 'Error deleting account!\n' + Style.RESET_ALL)
            return result
        else:
            return -1 """