from sqlite3 import dbapi2
from models.model_base import Model
from db.db_operations import DatabaseOperations
from colorama import Fore, Style, init

class Credentials(Model):
    """
    This class defines the Credentials model, which stores user authentication and authorization details,
    extending the functionality provided by the Model class.
    """

    def __init__(self, id, username, password, role, public_key, private_key, temp_code, temp_code_validity, publicKey, privateKey, update_datetime, creation_datetime, db):       
        """
        Initializes a new instance of Credentials class with the provided user credentials details.

        Parameters:
        - id: Unique identifier for the credentials record
        - username: Username associated with the credentials
        - password: Password for user authentication
        - role: The role assigned to the user ('USER_CERTIFIER', 'USER_ACTOR', 'ADMIN')
        - public_key: ...
        - private_key: ...
        - temp_code: Temporary code for two-factor authentication (optional)
        - temp_code_validity: Expiration  date/time for the temporary code (optional)
        - publicKey: ...
        - privateKey ....
        - update_datetime: Timestamp for when the credentials were last updated
        - creation_datetime: Timestamp for when the credentials were created
        - db: DatabaseOperations instance to interact with the database

        non so se public_key sia la chiave pubblica del wallet o la chiave pubblica per l'autenticazione, comunque commento per 
        quello della blockchain è: "The public key associated with the user for accessing their wallet on the blockchain", 
        private blockchain key "The private key associated with the user for accessing their wallet on the blockchain; kept secure and private"

        l'altro è public: "The public key used for the user’s authentication on the platform (separate from the blockchain key)" ?? separato o no poi?
        private : "The private key used for the user’s authentication on the platform (separate from the blockchain key)" 
        """
        super().__init__()
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.public_key = public_key
        self.private_key = private_key
        self.temp_code = temp_code
        self.temp_code_validity = temp_code_validity
        self.publicKey = publicKey
        self.privateKey = privateKey
        self.update_datetime = update_datetime
        self.creation_datetime = creation_datetime
        self.db = db

    # Getter methods for each attribute
    def get_id(self):
        return self.id

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_role(self):
        return self.role

    def get_public_key(self):
        return self.public_key

    def get_private_key(self):
        return self.private_key

    def get_temp_code(self):
        return self.temp_code

    def get_temp_code_validity(self):
        return self.temp_code_validity

    def get_publicKey(self):
        return self.publicKey

    def get_privateKey(self):
        return self.privateKey

    def get_update_datetime(self):
        return self.update_datetime

    def get_creation_datetime(self):
        return self.creation_datetime
        
    def save(self):
        """
        Saves a new or updates an existing Credentials record in the database.
        Implements SQL queries to insert or update credentials based on the presence of an ID.
        """
        if self.id is None:
            # Insert new credentials record
            result = self.db.register_creds(
                self.username, self.password, self.role,
                self.public_key, self.private_key,
                self.temp_code, self.temp_code_validity
            )
            if result == 0:
                self.id = self.cur.lastrowid
        else:
            # Update existing credentials record
            result = self.db.update_creds(self.username, self.password, self.role, self.public_key, self.private_key, 
                              self.temp_code, self.temp_code_validity, self.publicKey, self.privateKey, self.id)
        if result == 0:
            print(Fore.GREEN + 'Information saved correctly!\n' + Style.RESET_ALL)
        else:
            print(Fore.RED + 'Error saving information!\n' + Style.RESET_ALL)
        return result

    def delete(self):
        """
        Deletes a Credentials record from the database based on its ID.
        """
        if self.id is not None:
            result = self.db.delete_creds(self.id)
            if result == 0:
                print(Fore.GREEN + 'Information deleted correctly!\n' + Style.RESET_ALL)
            else:
                print(Fore.RED + 'Error deleting information!\n' + Style.RESET_ALL)
            return result
        else:
            return -1


   