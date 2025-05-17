import re
from datetime import datetime
from colorama import Fore, Style, init
from db.db_operations import DatabaseOperations
from session.session import Session

#2FA debgu
import smtplib
import random
import ssl
from email.message import EmailMessage

from models.credentials import Credentials
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

# ---------- ACCOUNTS ----------

    def insert_actor_info(self, role: str, username: str, name: str, lastname: str, actorLicense: int, residence: str, birthdayPlace: str, birthday: str, mail: str, phone: str):
        """
        Inserts a new actor record into the Accounts table in the database.

        Args:
            role (str): The role of the actor.
            username (str): The username of the actor.
            name (str): The first name of the actor.
            lastname (str): The last name of the actor.
            actorLicense (int): The license number of the actor.
            residence (str): The residence of the actor.
            birthdayPlace (str): The birth place of the actor.
            birthday (str): The birthday of the actor (format YYYY-MM-DD).
            mail (str): The email address of the actor.
            phone (str): The phone number of the actor.

        Returns:
            int: 0 if the insertion was successful, -1 if an integrity error occurred, such as violating unique constraints
                or foreign key references.
        """
        if not self.db_ops.check_valid_licence(role, actorLicense):
               return -2  # Or another code indicating license failure
    
        insertion_code = self.db_ops.insert_actor(role, username, name, lastname, actorLicense, residence, birthdayPlace, birthday, mail, phone)

        if insertion_code == 0:
            user = self.get_user_by_username(username)
            self.session.set_user(user)
            print(Fore.GREEN + 'DONE' + Style.RESET_ALL)

        return insertion_code

    def update_actor_info(self, user):
        """
        Updates the information of an existing account in the database.

        This method updates multiple fields of an account based on the given account ID.
        All fields are replaced with the new provided values.

        Parameters:
            username (str): The updated username.
            name (str): The updated first name.
            lastname (str): The updated last name.
            birthday (str): The updated date of birth (in string or date format).
            birth_place (str): The updated place of birth.
            residence (str): The updated residence address.
            phone (str): The updated phone number.
            mail (str): The updated email address.
            id (int): The ID of the account to update.

        Returns:
            int: 0 if the update is successful, -1 if a database error occurs.
        """
        return self.db_ops.update_account(user.get_username(), user.get_name(), user.get_lastname(),  user.get_birthday(), user.get_birth_place(), user.get_residence(),
                                         user.get_phone(), user.get_mail(), user.get_id())

    def get_users(self):
        """
        Retrieves all user records from the Accounts table.

        Returns:
            list: A list of Accounts instances representing all users in the system.
        """
        return self.db_ops.get_users()

    def get_user_by_username(self, username):
        """
        Retrieves a user's detailed information from table Account.

        Args:
            username (str): The username of the user.

        Returns:
            Accounts: An instance of the Accounts class if the user exists, otherwise, None.
        """
        return self.db_ops.get_user_by_username(username)

    def check_unique_email(self, mail):
        """
        Checks if an email address is unique within the Accounts table in the database.

        Args:
            mail (str): The email address to check for uniqueness.

        Returns:
            int: 0 if the email address is not found in the Accounts records (unique), -1 if it is found (not unique).
        """
        return self.db_ops.check_unique_email(mail)

    def check_unique_phone_number(self, phone):
        """
        Checks if a phone number is unique within the Accounts table in the database.

        Args:
            phone (str): The phone number to check for uniqueness.

        Returns:
            int: 0 if the phone number is not found in any records (unique), -1 if it is found (not unique).
        """
        return self.db_ops.check_unique_phone_number(phone)

# ---------- END ACCOUNTS ----------

# ---------- ACCOUNTS_ACTIVITIES ----------

    def register_account_activities(self, username, activity_id):
        """
        Inserts a new association between a user account and an activity into the Accounts_Activities table.

        Args:
            username (str): The username of the account.
            activity_id (int): The ID of the activity to associate with the user.

        Returns:
            int: 0 if the insertion is successful.
            int: -1 if a database integrity error occurs (e.g., duplicate entry).
        """
        return self.db_ops.register_account_activities(username, activity_id)

# ---------- END ACCOUNTS_ACTIVITIES ----------

# ---------- ACTIVITIES ----------

    def register_activities(self, activity_type, description):
        """
        Inserts a new activity record into the Activities table.

        Args:
            type (str): The type/category of the activity.
            description (str): A description of the activity.

        Returns:
            int: The ID of the newly inserted activity if successful.
            int: -1 if a database integrity error occurs.
        """
        return self.db_ops.register_activities(activity_type, description)

# ---------- END ACTIVITIES ----------

# ---------- CREDENTIALS ----------

    def registration(self, username: str, password: str, public_key: str, private_key: str):
        """
        Registers a new credentials record in the database.

        Checks if the username is available, then hashes the password,
        encrypts the private key with the password, and inserts all data into the Credentials table.

        Args:
            username (str): The username to register.
            password (str): The plain-text password to be hashed and stored.
            public_key (str): The public key associated with the user.
            private_key (str): The private key to be encrypted and stored.
            temp_code (str, optional): Temporary code for authentication or recovery.
            temp_code_validity (datetime, optional): Expiry datetime of the temporary code.

        Returns:
            int: 0 if registration succeeds, -1 if username already exists or on database error.
        """
        registration_code = self.db_ops.register_creds(username, password, public_key, private_key)

        return registration_code

    def update_password(self, username, password):
        """
        Changes the password for a given username by hashing the new password
        and updating the corresponding record in the Credentials table.

        Args:
            username (str): The username of the account to update.
            new_pass (str): The new plain-text password to be hashed and stored.

        Returns:
            int: 0 if the password update was successful, -1 if an error occurred.
        """
        return self.db_ops.change_password(username, password)

    def delete_creds(self, id):
        """
        Deletes a credentials record from the database based on its ID.

        Args:
            id (int): The ID of the credentials record to delete.

        Returns:
            int: 0 if the deletion is successful,
                 -1 if no record was found with the given ID or if an error occurs.
        """
        return self.db_ops.delete_creds(id)

    def get_credentials_id_by_username(self, username):
        """
        Retrieves the ID of the credentials record associated with the given username.

        Args:
            username (str): The username whose credentials ID is to be retrieved.

        Returns:
            int or None: The ID of the credentials record if found, otherwise None.
        """
        return self.db_ops.get_credentials_id_by_username(username)

    def get_public_key_by_username(self, username):
        """
        Retrieve the public key for a given username from the Credentials table.

        Args:
            username (str): The username of the user whose public key is to be retrieved.

        Returns:
            str: The public key of the user if found, None otherwise.
        """
        return self.db_ops.get_public_key_by_username(username)

    def get_helpers(self):
        """
        Retrieves the public keys of all users who are considered potential helpers.
    
        Specifically, it selects public keys from the Credentials table for users
        whose account type is not 'CERTIFIER'.
    
        Returns:
            list of str: A list containing the public keys of potential helpers.
        """
        return self.db_ops.get_helpers()

    def get_username_by_public_key(self, public_key):
        """
        Retrieves the username associated with the given public key.

        Args:
            public_key (str): The public key to look up.

        Returns:
            str or None: The username linked to the public key if found, otherwise None.
        """
        return self.db_ops.get_username_by_public_key(public_key)

    def check_username(self, username):
        """
        Check if an username is unique within the Credentials table in the database.

        Args:
            username (str): The username to check for uniqueness.

        Returns:
            int: 0 if the email address is not found in the Accounts records (unique), -1 if it is found (not unique).
        """
        return self.db_ops.check_username(username)

    def check_credentials(self, username, password):
        """
        Verifies if the provided username and password match a record in the database.

        Parameters:
            username (str): The username to check.
            password (str): The plain-text password to verify.

        Returns:
            bool: True if the credentials are valid, False otherwise.
        """
        return self.db_ops.check_credentials(username=username, password=password)

    def check_keys(self, public_key, private_key):
        """
        Checks if either a public key or a private key already exists in the Credentials table.

        Args:
            public_key (str): The public key to check against existing entries in the database.
            private_key (str): The private key to check against existing entries in the database.

        Returns:
            bool: True if either the public or private key is found in the database (indicating they are not unique),
                  False if neither key is found (indicating they are unique) or an exception occurs during the query.
        """
        return self.db_ops.key_exists(public_key, private_key)

# ---------- END CREDENTIALS ----------

# ---------- CRON_ACTIVITIES ----------
    def register_cron_activity(self, description, username, state, activity_id, co2_reduction):
        """
        Inserts a new record into the Cron_Activities table.

        Args:
            description (str): Description of the cron activity.
            username (str): Username associated with the activity.
            state (int): State/status of the activity (e.g., 0 for pending, 1 for processed).
            activity_id (int): ID referencing the original activity.
            co2_reduction (float): Amount of CO2 reduction attributed to this activity.

        Returns:
            int: 0 if insertion is successful.
            int: -1 if a database integrity error occurs, printing the error message.
        """
        return self.db_ops.register_cron_activity(description,  username, state, activity_id, co2_reduction)

    def update_activity_state(self, activitie_id):
        """
        Updates the state of a specific activity identified by its activity_id.

        Args:
            activitie_id (int): The unique identifier of the activity to update.
            state (int): The new state value to set for the activity.

        Returns:
            int: 0 if the update is successful, -1 if a database error occurs.
        """
        state = self.db_ops.get_state_by_activity(activitie_id)

        if state == 0:
            return self.db_ops.update_activity_state(activitie_id, 1)
        elif state == 1:
            return self.db_ops.update_activity_state(activitie_id, 2)

    def get_activities_to_be_processed(self):
        """
        Retrieves all activities that have not been processed yet.

        Returns:
            list: A list of Cron_Activities objects representing unprocessed activities.
        """
        return self.db_ops.get_activities_to_be_processed()

    def get_activities_by_username(self, username):
        """
        Retrieves all activities associated with a given username.

        Args:
            username (str): The username for which to retrieve activities.

        Returns:
            list: A list of Cron_Activities objects related to the given user.
        """
        return self.db_ops.get_activities_by_username(username)

    def get_activities_to_be_processed_by_username(self, username):
        """
        Retrieves all activities assigned to the given username that are pending processing.

        Args:
            username (str): The username to filter activities by.

        Returns:
            list of Cron_Activities: A list of Cron_Activities objects representing activities
                                     with state = 0 (to be processed) for the specified user.
        """
        return self.db_ops.get_activities_to_be_processed_by_username(username)

    def get_activities_processed_by_username(self, username):
        """
        Retrieves all activities that have been processed for a given username.

        Args:
            username (str): The username to filter activities by.

        Returns:
            list of Cron_Activities: A list of Cron_Activities objects representing activities
                                     with state = 1 (processed) for the specified user.
        """
        return self.db_ops.get_activities_processed_by_username(username)

    def get_co2Amount_by_activity(self, activity_id):
        """
        Retrieves the total amount of CO2 reduction associated with a specific activity.

        Args:
            activity_id (int): The unique identifier of the activity.

        Returns:
            float or None: The CO2 reduction amount for the given activity_id,
                           or None if no matching activity is found.
        """
        return self.db_ops.get_co2Amount_by_activity(activity_id)

# ---------- END CRON_ACTIVITIES ----------

# ---------- PRODUCTS ----------

    def create_product(self, name, category, co2Emission, nft_token_id):
        """
        Inserts a new product record into the Products table.

        Parameters:
            name (str): The name of the product.
            category (str): The category to which the product belongs.
            co2Emission (float): The CO2 emissions associated with the product.
            nft_token_id (int): The ID of the associated NFT token.

        Returns:
            int: 0 if the insertion is successful, -1 if a database integrity error occurs.
        """
        return self.db_ops.insert_product(name, category, co2Emission, nft_token_id)

    def update_product(self, product_id, co2Emission):
        """
        Updates the CO2 emission data of an existing product in the Products table.

        Parameters:
            product_id (int): The ID (nftID) of the product to update.
            co2Emission (float, optional): The new CO2 emission value to set. If None, no update is performed.

        Returns:
            int:
                0  -> if the update was successful,
               -1 -> if no record was found, no change occurred, or a database error happened.
        """
        return self.db_ops.update_product(product_id, co2Emission)

# ---------- END PRODUCTS ----------

# ---------- TRANSACTIONS ----------

    def insert_transaction(self, username_from, username_to, amount, type, tx_hash):
        """
        Inserts a new transaction record into the Transactions table.

        Args:
            username_from (str): The username of the sender.
            username_to (str): The username of the receiver.
            amount (float): The amount involved in the transaction.
            type (str): The type/category of the transaction.
            tx_hash (str): The unique transaction hash identifier.

        Returns:
            int: 0 if the insertion is successful, -1 if a database integrity error occurs.
        """
        return self.db_ops.insert_transaction(username_from, username_to, amount, type, tx_hash)

    def get_user_transactions(self, user_username):
        """
        Retrieves all transactions involving a specific user, either as sender or receiver.

        Args:
            user_username (str): The username of the user whose transactions are to be retrieved.

        Returns:
            list of Transaction: A list of Transaction objects ordered by timestamp descending.
        """
        return self.db_ops.get_user_transactions(user_username)

# ---------- END TRANSACTIONS ---------- 


    def login(self, username: str, password: str):
        """
        Attempts to log a user in by validating credentials and handling session attempts.
        
        :param username: The user's username.
        :param password: The user's password.
        :return credential object.
        """
        if(self.check_attempts() and self.db_ops.check_credentials(username, password)):
            creds: Credentials = self.db_ops.get_creds_by_username(username)
            user_role = self.get_user_by_username(username).get_type()
            user = creds.get_username
            self.session.set_user(user)
            return 1, user_role
        elif self.check_attempts():
            self.session.increment_attempts()
            if self.session.get_attempts() == self.__n_attempts_limit:
                self.session.set_error_attempts_timeout(self.__timeout_timer)
            return -2, None
        else:
            return -3, None

    def check_attempts(self):
        if self.session.get_attempts() < self.__n_attempts_limit:
            return True
        else:
            return False
        
    #2fa debug and test

    # mailer
    def send_2fa_code(email_address, code):
        sender_email = ""
        sender_password = ""  

        msg = EmailMessage()
        msg.set_content(f"Your verification code is: {code}")
        msg["Subject"] = "Your Verification Code"
        msg["From"] = sender_email
        msg["To"] = email_address

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)

    # generate random atp code
    def generate_code():
        return str(random.randint(100000, 999999))
    #end debug 2fa     

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








   








    

