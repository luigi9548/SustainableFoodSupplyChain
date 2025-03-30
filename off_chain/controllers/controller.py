import re
from datetime import datetime
from colorama import Fore, Style, init
from db.db_operations import DatabaseOperations
from session.session import Session
#from models.credentials import Credentials

class Controller:
    """
    Controller handles user and data interactions with the database.
    """
    init(convert=True)

    def __init__(self, session: Session):
        """
        Initialize the Controller with a session object and set up the database operations.
        
        :param session: The session object to manage user sessions and login attempts.
        """
        self.db_ops = DatabaseOperations()
        self.session = session
        self.__n_attempts_limit = 5 # Maximum number of login attempts before lockout.
        self.__timeout_timer = 180 # Timeout duration in seconds.

    def registration(self, username: str, password: str, role: str, public_key: str, private_key: str):
        """
        Registers a new user in the database with the given credentials.
        
        :param username: The user's username.
        :param password: The user's password.
        :param role: The user's role in the system.
        :param public_key: The user's public key.
        :param private_key: The user's private key.
        :return: A registration code indicating success or failure.
        """
        registration_code = self.db_ops.register_creds(username, password, role, public_key, private_key)

        return registration_code

    def insert_actor_info(self, role: str, username: str, name: str, lastname: str, actorLicense: int, residence: str, birthdayPlace: str, birthday: str, mail: str, phone: str):
        """
        Inserts actor information into the database.

        :param role: The role of the actor.
        :param username: The username of the actor.
        :param name: The first name of the actor.
        :param lastname: The last name of the actor.
        :param actorLicense: The license number of the actor.
        :param residence: The residence of the actor.
        :param birthdayPlace: The birth place of the actor.
        :param birthday: The birthday of the actor (format YYYY-MM-DD).
        :param mail: The email address of the actor.
        :param phone: The phone number of the actor.
        :return: An insertion code indicating success (0) or failure.
        """
        insertion_code = self.db_ops.insert_actor(role, username, name, lastname, actorLicense, residence, birthdayPlace, birthday, mail, phone)

        if insertion_code == 0:
            user = self.get_user_by_username(username)
            self.session.set_user(user)
            print(Fore.GREEN + 'DONE' + Style.RESET_ALL)

        return insertion_code

    def check_null_info(self, info):
        """
        Checks if the provided information is non-null (or truthy).

        :param info: The information to be checked. This can be any type, including strings, numbers, or other objects.
        :return: Returns True if the information is non-null/non-empty (truthy), False otherwise (falsy).
        """
        if info:
            return True
        else:
            return False

    def check_birthdate_format(self, date_string):
        """
        Validates that a provided date string is in the correct format ('YYYY-MM-DD') and is a date in the past.

        :param date_string: The date string to validate, expected to be in the format 'YYYY-MM-DD'.
        :return: Returns True if the date string is correctly formatted and represents a past date; 
        returns False if the date is not in the correct format or is in the future.
        """
        try:
            date = datetime.strptime(date_string, '%Y-%m-%d')
            current_date = datetime.now()
            if date < current_date:
                return True
            else:
                return False
        except ValueError:
            return False

    def check_email_format(self, email):
        """
        Validates that a given email address conforms to a standard email format.

        :param email: The email string to validate.
        :return: Returns True if the email matches the standard email format pattern.
                 Returns False if the email does not match this pattern.
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, email):
            return True
        else:
            return False

    def check_phone_number_format(self, phone_number):
        """
        Validates that a given phone number is in a correct numerical format and within the expected length range.

        :param phone_number: The phone number string to validate. The number may contain spaces or hyphens.
        :return: Returns True if the phone number contains only digits (after removing spaces and hyphens) 
                 and if its length is between 7 and 15 characters. Returns False otherwise.
        """
        if phone_number.replace('-', '').replace(' ', '').isdigit():
            if 7 <= len(phone_number) <= 15:
                return True
        return False

    def check_unique_phone_number(self, phone):
        return self.db_ops.check_unique_phone_number(phone)

    def check_unique_email(self, mail):
        return self.db_ops.check_unique_email(mail)

    def check_keys(self, public_key, private_key):
        return self.db_ops.key_exists(public_key, private_key)

    def check_username(self, username):
        return self.db_ops.check_username(username)

    def get_public_key_by_username(self, username):
        return self.db_ops.get_public_key_by_username(username)

    def get_user_by_username(self, username):
        return self.db_ops.get_user_by_username(username)

    def update_actor_info(self, user):
        return self.db_ops.update_account(user.get_username(), user.get_name(), user.get_lastname(),  user.get_birthday(), user.get_birth_place(), user.get_residence(),
                                         user.get_phone(), user.get_mail(), user.get_id())

    def get_activities_to_be_processed(self):
        return self.db_ops.get_activities_to_be_processed()

    def get_activities_by_username(self, username):
        return self.db_ops.get_activities_by_username(username)

    def get_users(self):
        return self.db_ops.get_users()

    def create_product(self, name, category, co2Emission, sensorId):
        return self.db_ops.insert_product(name, category, co2Emission, sensorId)

    #def update_product(self, )