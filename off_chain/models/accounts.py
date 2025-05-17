from models.model_base import Model

class Accounts(Model):
    """
    This class defines the Account model, which stores user account details,  
    extending the functionality provided by the Model class.
    """

    def __init__(self, id, username, type, name, licence_id, lastname, birthday, birth_place, residence, phone, mail):
        """
        Initializes a new instance of Account class with the provided account  details.

        Parameters:
        - id: Unique identifier for the account record
        - username: The username associated with the account
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
        self.username = username
        self.type = type
        self.name = name
        self.licence_id = licence_id
        self.lastname = lastname
        self.birthday = birthday
        self.birth_place = birth_place
        self.residence = residence
        self.phone = phone
        self.mail = mail

    # Getter methods for each attribute
    def get_id(self):
        return self.id

    def get_username(self):
        return self.username

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
      