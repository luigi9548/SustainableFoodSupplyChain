import datetime
import sqlite3
import os
import hashlib
import base64
from typing import Self
from cryptography.fernet import Fernet
from colorama import Fore, Style, init
from config import config
from models.accounts import Accounts
from models.cron_activities import Cron_Activities
from models.credentials import Credentials
from models.transaction import Transaction

class DatabaseOperations:
    """
    Handles all interactions with the database for user data manipulation and retrieval.
    """
    init(convert=True)

    def __init__(self):
        self.conn = sqlite3.connect(config.config["db_path"])
        self.cur = self.conn.cursor()
        self._create_new_table()
        self.insert_test_records()
        self.today_date = datetime.date.today().strftime('%Y-%m-%d')

    # Metodo da eliminare, utilizzato temporaneamente per debugging
    def _create_new_table(self):
        """
        Creates necessary tables in the database if they are not already present.
        This ensures that the database schema is prepared before any operations are performed.
        """
        #self.cur.execute("DROP TABLE IF EXISTS Credentials")
        #self.cur.execute("DROP TABLE IF EXISTS Accounts")
        self.cur.execute("DROP TABLE IF EXISTS Activities")
        self.cur.execute("DROP TABLE IF EXISTS Accounts_Activities")
        self.cur.execute("DROP TABLE IF EXISTS Cron_Activities")
        self.cur.execute("DROP TABLE IF EXISTS Licences")
        self.cur.execute("DROP TABLE IF EXISTS Products")
        self.cur.execute("DROP TABLE IF EXISTS Transactions")

        self.cur.execute('''CREATE TABLE IF NOT EXISTS Credentials (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        public_key TEXT NOT NULL,
                        private_key TEXT NOT NULL,
                        temp_code TEXT,
                        temp_code_validity DATETIME,
                        update_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        creation_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                        );''')

        # trigger for automatic update of update_datetime
        self.cur.execute('''CREATE TRIGGER IF NOT EXISTS update_Credentials_timestamp
                        AFTER UPDATE ON Credentials
                        FOR EACH ROW
                        BEGIN
                        UPDATE Credentials SET update_datetime = CURRENT_TIMESTAMP WHERE id = OLD.id;
                        END;''')

        # licence it's mandatory for each actor
        self.cur.execute('''CREATE TABLE IF NOT EXISTS Accounts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        type TEXT CHECK(type IN ('FARMER', 'CARRIER', 'SELLER', 'PRODUCER', 'CERTIFIER')) NOT NULL,
                        name TEXT NOT NULL,
                        licence_id INTEGER NOT NULL,
                        lastname TEXT NOT NULL,
                        birthday TEXT NOT NULL,
                        birth_place TEXT,
                        residence TEXT,
                        phone TEXT,
                        mail TEXT,
                        FOREIGN KEY (username) REFERENCES Credentials(username),
                        FOREIGN KEY (licence_id) REFERENCES Licences(id)
                        );''')

        # Licences table to verufy the authenticity of role and mitigate misuese (aggiorno io le tabelle sul misuso, in fase di inserimento utente verifichiamo al sua licenza)
        self.cur.execute('''CREATE TABLE IF NOT EXISTS Licences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT CHECK(type IN ('FARMER', 'CARRIER', 'SELLER', 'PRODUCER', 'CERTIFIER')) NOT NULL,
                    licence_number TEXT NOT NULL UNIQUE
                    );''')


        self.cur.execute('''CREATE TABLE IF NOT EXISTS Activities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        type TEXT CHECK(type IN ('investment in a project for reduction', 'performing an action')) NOT NULL,
                        description TEXT NOT NULL
                        );''')


        self.cur.execute('''CREATE TABLE IF NOT EXISTS Accounts_Activities (
                        username TEXT NOT NULL,
                        activity_id INTEGER NOT NULL,
                        PRIMARY KEY (username, activity_id),
                        FOREIGN KEY (username) REFERENCES Credentials(username),
                        FOREIGN KEY (activity_id) REFERENCES Activities(id)
                        );''')


        self.cur.execute('''CREATE TABLE IF NOT EXISTS Cron_Activities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        description TEXT NOT NULL,
                        username TEXT NOT NULL,
                        update_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        creation_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        state INTEGER NOT NULL CHECK(state IN (0, 1, 2)),
                        activity_id INTEGER NOT NULL,
                        co2_reduction DECIMAL NOT NULL,
                        FOREIGN KEY (username) REFERENCES Credentials(username),
                        FOREIGN KEY (activity_id) REFERENCES Activities(id)
                        );''')

        # trigger for automatic update of update_datetime
        self.cur.execute('''CREATE TRIGGER IF NOT EXISTS update_Cron_Activities_timestamp
                        AFTER UPDATE ON Cron_Activities
                        FOR EACH ROW
                        BEGIN
                        UPDATE Cron_Activities SET update_datetime = CURRENT_TIMESTAMP WHERE id = OLD.id;
                        END;''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS Products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        category TEXT CHECK(category IN ('FRUIT', 'MEAT', 'DAIRY')) NOT NULL,
                        co2Emission INTEGER NOT NULL,
                        nftID INTEGER NOT NULL,
                        harvestDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        update_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                        );''')

        # trigger for automatic update of update_datetime
        self.cur.execute('''CREATE TRIGGER IF NOT EXISTS update_Products_timestamp
                        AFTER UPDATE ON Products
                        FOR EACH ROW
                        BEGIN
                        UPDATE Products SET update_datetime = CURRENT_TIMESTAMP WHERE id = OLD.id;
                        END;''')

        self.cur.execute('''CREATE TABLE Transactions (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         username_from TEXT,
                         username_to TEXT,
                         amount INTEGER NOT NULL,
                         type TEXT CHECK(type IN ('MINT', 'BURN', 'TRANSFER')) NOT NULL,
                         tx_hash TEXT,
                         timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                         );
                         ''')

        self.conn.commit()

    def insert_test_records(self):
        self.cur.execute('''INSERT INTO Licences (type, licence_number) VALUES
                            ('FARMER', '2001'),
                            ('CARRIER', '2002'),
                            ('SELLER', '2003'),
                            ('PRODUCER', '2004'),
                            ('CERTIFIER', '2005');''')

        self.cur.execute('''INSERT INTO Activities (type, description) VALUES
                            ('investment in a project for reduction', 'Investing in solar panels'),
                            ('performing an action', 'Using electric vehicles for transport');''')

        self.cur.execute('''INSERT INTO Accounts_Activities (username, activity_id) VALUES
                            ('farmer_user', 1),
                            ('carrier_user', 2);''')

        self.cur.execute('''INSERT INTO Cron_Activities (description, username, state, activity_id, co2_reduction) VALUES
                            ('Solar panel investment', 'farmer_user', 0, 1, 50.0),
                            ('Electric vehicle implementation', 'carrier_user', 0, 2, 30.5);''')

        self.cur.execute('''INSERT INTO Products (name, category, co2Emission, nftID) VALUES
                            ('Apple', 'FRUIT', 10, 0),
                            ('Beef', 'MEAT', 50, 1),
                            ('Cheese', 'DAIRY', 20, 2);''')

        self.conn.commit()

# ---------- ACCOUNTS ----------

    def insert_actor(self, role, username, name, lastname, actorLicense, residence, birthdayPlace, birthday, mail, phone):
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

        Exceptions:
            sqlite3.IntegrityError: Catches and handles any integrity errors during the insertion process, which typically occur
                                    due to violation of database constraints like unique keys or foreign key constraints.
        """
        try:
            self.cur.execute("""
                            INSERT INTO Accounts
                            (username, type, name, licence_id, lastname, birthday, birth_place, residence, phone, mail) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """,
                            (
                                username,
                                role,
                                name,
                                actorLicense,
                                lastname,
                                birthday,
                                birthdayPlace,
                                residence,
                                phone,
                                mail
                            ))
            self.conn.commit()
            return 0
        except sqlite3.IntegrityError as e:
            return -1
 
    def update_account(self, username, name, lastname, birthday, birth_place, residence, phone, mail, id):
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
        try:
            self.cur.execute("""
            UPDATE Accounts 
            SET username = ?, name = ?, lastname = ?, birthday = ?, 
                birth_place = ?, residence = ?, phone = ?, mail = ? 
            WHERE id = ?""",
            (username, name, lastname, birthday, birth_place, residence, phone, mail, id))
            self.conn.commit()
            return 0
        except sqlite3.Error:
            return -1

    def get_users(self):
        """
        Retrieves all user records from the Accounts table.

        Returns:
            list: A list of Accounts instances representing all users in the system.
        """
        self.cur.execute("SELECT * FROM Accounts")

        users = [Accounts(id, username, role, name, licence_id, lastname, birthday, birth_place, residence, phone, mail)
                 for id, username, role, name, licence_id, lastname, birthday, birth_place, residence, phone, mail in self.cur.fetchall()]
        return users

    def get_user_by_username(self, username):
        """
        Retrieves a user's detailed information from table Account.

        Args:
            username (str): The username of the user.

        Returns:
            Accounts: An instance of the Accounts class if the user exists, otherwise, None.
        """
        user = self.cur.execute("""
                                    SELECT *
                                    FROM Accounts
                                    WHERE Accounts.username = ?""", (username,)).fetchone()

        if user is not None:
            return Accounts(*user)
        return None

    def check_unique_email(self, mail):
        """
        Checks if an email address is unique within the Accounts table in the database.

        Args:
            mail (str): The email address to check for uniqueness.

        Returns:
            int: 0 if the email address is not found in the Accounts records (unique), -1 if it is found (not unique).
        """
        query_accounts = "SELECT COUNT(*) FROM Accounts WHERE mail = ?"
        self.cur.execute(query_accounts, (mail,))
        count_accounts = self.cur.fetchone()[0]

        if count_accounts == 0:
            return 0
        else:
            return -1

    def check_unique_phone_number(self, phone):
        """
        Checks if a phone number is unique within the Accounts table in the database.

        Args:
            phone (str): The phone number to check for uniqueness.

        Returns:
            int: 0 if the phone number is not found in any records (unique), -1 if it is found (not unique).
        """
        query_accounts = "SELECT COUNT(*) FROM Accounts WHERE phone = ?"
        self.cur.execute(query_accounts, (phone,))
        count_accounts = self.cur.fetchone()[0]

        if count_accounts == 0:
            return 0
        else:
            return -1

# ---------- END ACCOUNTS ----------

# ---------- ACCOUNTS_ACTIVITIES

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
        try:
            self.cur.execute("INSERT INTO Accounts_Activities (username, activity_id) VALUES (?, ?)",
                           (username, activity_id))
            self.conn.commit()
            return 0
        except sqlite3.IntegrityError:
            return -1

# ---------- END ACCOUNTS_ACTVITIES ----------

# ---------- ACTIVITIES ---------

    def register_activities(self, type, description):
        """
        Inserts a new activity record into the Activities table.

        Args:
            type (str): The type/category of the activity.
            description (str): A description of the activity.

        Returns:
            int: The ID of the newly inserted activity if successful.
            int: -1 if a database integrity error occurs.
        """
        try:
            self.cur.execute("""
            INSERT INTO Activities (type, description) 
            VALUES (?, ?)""",
             (type, description))
            activity_id = self.cur.lastrowid 
            self.conn.commit()
            return activity_id
        except sqlite3.IntegrityError:
            return -1

# ---------- END ACTIVITIES ----------

# ---------- CREDENTIALS ----------

    def register_creds(self, username, password, public_key, private_key, temp_code=None, temp_code_validity=None):
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
        try:
            if self.check_username(username) == 0:
                obfuscated_private_k = self.encrypt_private_k(private_key, password)
                hashed_passwd = self.hash_function(password)
                self.cur.execute("""
                    INSERT INTO Credentials (username, password, public_key, private_key, temp_code, temp_code_validity)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (username, hashed_passwd, public_key, obfuscated_private_k, temp_code, temp_code_validity))
                self.conn.commit()
                return 0
            else:
                return -1
        except sqlite3.IntegrityError as e:
            print(Fore.RED + f'Internal error: {e}' + Style.RESET_ALL)
            return -1

    def change_password(self, username, new_pass):
        """
        Changes the password for a given username by hashing the new password
        and updating the corresponding record in the Credentials table.

        Args:
            username (str): The username of the account to update.
            new_pass (str): The new plain-text password to be hashed and stored.

        Returns:
            int: 0 if the password update was successful, -1 if an error occurred.
        """
        new_hash = self.hash_function(new_pass)
        try:
            self.cur.execute("UPDATE Credentials SET password = ? WHERE username = ?", (new_hash, username))
            self.conn.commit()
            return 0
        except Exception:
            return -1

    def delete_creds(self, id):
        """
        Deletes a credentials record from the database based on its ID.

        Args:
            id (int): The ID of the credentials record to delete.

        Returns:
            int: 0 if the deletion is successful,
                 -1 if no record was found with the given ID or if an error occurs.
        """
        try:
            self.cur.execute("DELETE FROM Credentials WHERE id = ?", (id,))
            self.conn.commit()

            if self.cur.rowcount > 0:
                print(Fore.GREEN + "Information deleted correctly!\n" + Style.RESET_ALL)
                return 0
            else:
                print(Fore.YELLOW + "No record found with the given ID.\n" + Style.RESET_ALL)
                return -1

        except sqlite3.Error as e:
            print(Fore.RED + f'Error deleting credentials: {e}' + Style.RESET_ALL)
            return -1

    def get_credentials_id_by_username(self, username):
        """
        Retrieves the ID of the credentials record associated with the given username.

        Args:
            username (str): The username whose credentials ID is to be retrieved.

        Returns:
            int or None: The ID of the credentials record if found, otherwise None.
        """
        try:
            self.cur.execute("SELECT id FROM Credentials WHERE username = ?", (username,))
            result = self.cur.fetchone()
            if result:
                return result[0]
            else:
                return None
        except sqlite3.Error as e:
            print(Fore.RED + f"Error retrieving credentials ID: {e}" + Style.RESET_ALL)
            return None

    def get_creds_by_username(self, username):
        """
        Retrieves a user's credentials from the Credentials table based on their username.

        Args:
            username (str): The username of the user whose credentials are to be retrieved.

        Returns:
            Credentials: A Credentials object containing the user's credentials if found.
            None: If no credentials are found for the given username.
        """
        creds = self.cur.execute("""
                                SELECT *
                                FROM Credentials
                                WHERE username=?""", (username,)).fetchone()
        if creds is not None:
            return Credentials(*creds)
        return None

    def get_public_key_by_username(self, username):
        """
        Retrieve the public key for a given username from the Credentials table.

        Args:
            username (str): The username of the user whose public key is to be retrieved.

        Returns:
            str: The public key of the user if found, None otherwise.
        """
        try:
            self.cur.execute("SELECT public_key FROM Credentials WHERE username = ?", (username,))
            result = self.cur.fetchone()
            if result:
                return result[0]  # Return the public key
            else:
                return None  # Public key not found
        except Exception as e:
            print(Fore.RED + f"An error occurred while retrieving public key: {e}" + Style.RESET_ALL)
            return None

    def get_helpers(self):
        """
        Retrieves the public keys of all users who are considered potential helpers.
    
        Specifically, it selects public keys from the Credentials table for users
        whose account type is not 'CERTIFIER'.
    
        Returns:
            list of str: A list containing the public keys of potential helpers.
        """
        self.cur.execute("""
                         SELECT c.public_key
                         FROM Credentials c
                         JOIN Accounts a ON c.username = a.username
                         WHERE a.type != 'CERTIFIER'
                         """)
        public_keys = [row[0] for row in self.cur.fetchall()]

        return public_keys

    def get_username_by_public_key(self, public_key):
        """
        Retrieves the username associated with the given public key.

        Args:
            public_key (str): The public key to look up.

        Returns:
            str or None: The username linked to the public key if found, otherwise None.
        """
        self.cur.execute(
            "SELECT username FROM Credentials WHERE public_key = ?", (public_key,))
        result = self.cur.fetchone()
        return result[0] if result else None

    def check_username(self, username):
        """
        Check if an username is unique within the Credentials table in the database.

        Args:
            username (str): The username to check for uniqueness.

        Returns:
            int: 0 if the email address is not found in the Accounts records (unique), -1 if it is found (not unique).
        """
        self.cur.execute("SELECT COUNT(*) FROM Credentials WHERE username = ?", (username,))
        return -1 if self.cur.fetchone()[0] > 0 else 0

    def check_credentials(self, username, password):
        """
        Verifies if the provided username and password match a record in the database.

        Parameters:
            username (str): The username to check.
            password (str): The plain-text password to verify.

        Returns:
            bool: True if the credentials are valid, False otherwise.
        """
        result = self.cur.execute("SELECT password FROM Credentials WHERE username = ?", (username,)).fetchone()
        if result:
            saved_hash = result[0]
            params = saved_hash.split('$')
            hashed_passwd = hashlib.scrypt(password.encode(), salt=bytes.fromhex(params[1]), n=2, r=8, p=1, dklen=64)
            return hashed_passwd.hex() == params[0]
        return False

    def key_exists(self, public_key, private_key):
        """
        Checks if either a public key or a private key already exists in the Credentials table.

        Args:
            public_key (str): The public key to check against existing entries in the database.
            private_key (str): The private key to check against existing entries in the database.

        Returns:
            bool: True if either the public or private key is found in the database (indicating they are not unique),
                  False if neither key is found (indicating they are unique) or an exception occurs during the query.
        
        Exceptions:
            Exception: Catches and prints any exception that occurs during the database operation, returning False.
        """
        try:
            query = "SELECT public_key, private_key FROM Credentials WHERE public_key=? OR private_key=?"
            existing_users = self.cur.execute(query, (public_key, private_key)).fetchall()
            return len(existing_users) > 0
        except Exception as e:
            print(Fore.RED + f"An error occurred: {e}" + Style.RESET_ALL)
            return False

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
        try:
            self.cur.execute("""
                INSERT INTO Cron_Activities (description, username, state, activity_id, co2_reduction)
                VALUES (?, ?, ?, ?, ?)""",
                (description, username, state, activity_id, co2_reduction)
            )
            self.conn.commit()
            return 0  # Success
        except sqlite3.IntegrityError as e:
            print(Fore.RED + f'Error inserting cron activity: {e}' + Style.RESET_ALL)
            return -1  # Error

    def update_activity_state(self, activitie_id, state):
        """
        Updates the state of a specific activity identified by its activity_id.

        Args:
            activitie_id (int): The unique identifier of the activity to update.
            state (int): The new state value to set for the activity.

        Returns:
            int: 0 if the update is successful, -1 if a database error occurs.
        """
        try:
            self.cur.execute("""
            UPDATE Cron_Activities 
            SET state = ? 
            WHERE activity_id = ?""",
            (state, activitie_id))
            self.conn.commit()
            return 0
        except sqlite3.Error:
            return -1

    def get_activities_to_be_processed(self):
        """
        Retrieves all activities that have not been processed yet.

        Returns:
            list: A list of Cron_Activities objects representing unprocessed activities.
        """
        self.cur.execute("SELECT * FROM Cron_Activities WHERE state = 0")

        activities = [Cron_Activities(id, description, username, update_datetime, creation_datetime, state, activity_id, co2_reduction)
                      for id, description, username, update_datetime, creation_datetime, state, activity_id, co2_reduction in self.cur.fetchall()]
        return activities

    def get_activities_by_username(self, username):
        """
        Retrieves all activities associated with a given username.

        Args:
            username (str): The username for which to retrieve activities.

        Returns:
            list: A list of Cron_Activities objects related to the given user.
        """
        self.cur.execute("SELECT * FROM Cron_Activities WHERE username = ?", (username,))

        activities = [Cron_Activities(id, description, username, update_datetime, creation_datetime, state, activity_id, co2_reduction)
                      for id, description, username, update_datetime, creation_datetime, state, activity_id, co2_reduction in self.cur.fetchall()]
        return activities

    def get_activities_to_be_processed_by_username(self, username):
        """
        Retrieves all activities assigned to the given username that are pending processing.

        Args:
            username (str): The username to filter activities by.

        Returns:
            list of Cron_Activities: A list of Cron_Activities objects representing activities
                                        with state = 0 (to be processed) for the specified user.
        """
        self.cur.execute("SELECT * FROM Cron_Activities WHERE username = ? AND state = 0", (username,))

        activities = [Cron_Activities(id, description, username, update_datetime, creation_datetime, state, activity_id, co2_reduction)
                      for id, description, username, update_datetime, creation_datetime, state, activity_id, co2_reduction in self.cur.fetchall()]

        return activities

    def get_activities_processed_by_username(self, username):
        """
        Retrieves all activities that have been processed for a given username.

        Args:
            username (str): The username to filter activities by.

        Returns:
            list of Cron_Activities: A list of Cron_Activities objects representing activities
                                     with state = 1 (processed) for the specified user.
        """
        self.cur.execute("SELECT * FROM Cron_Activities WHERE username = ? AND state = 1", (username,))

        activities = [Cron_Activities(id, description, username, update_datetime, creation_datetime, state, activity_id, co2_reduction)
                      for id, description, username, update_datetime, creation_datetime, state, activity_id, co2_reduction in self.cur.fetchall()]

        return activities

    def get_co2Amount_by_activity(self, activity_id):
        """
        Retrieves the total amount of CO2 reduction associated with a specific activity.

        Args:
            activity_id (int): The unique identifier of the activity.

        Returns:
            float or None: The CO2 reduction amount for the given activity_id,
                           or None if no matching activity is found.
        """
        co2Amount = self.cur.execute(
            "SELECT co2_reduction FROM Cron_Activities WHERE activity_id = ?", (activity_id,)).fetchone()
        return co2Amount[0] if co2Amount else None

    def get_state_by_activity(self, activity_id):
        """
        Retrieves the current state of a specific activity by its activity_id.

        Args:
            activity_id (int): The unique identifier of the activity.

        Returns:
            int or None: The state of the activity if found, otherwise None.
        """
        state = self.cur.execute(
            "SELECT state FROM Cron_Activities WHERE activity_id = ?", (activity_id,)).fetchone()
        return state[0] if state else None

# ---------- END CRON_ACTIVITIES ----------

# ---------- LICENCES ----------

    def check_valid_licence(self, role, licence_number):
        """
        Checks if a valid licence exists for a given role.
        """
        self.cur.execute("SELECT COUNT(*) FROM Licences WHERE type = ? AND licence_number = ?", (role, licence_number))
        return self.cur.fetchone()[0] > 0

# ---------- END LICENCES ----------

# ---------- PRODUCTS ----------

    def insert_product(self, name, category, co2Emission, nft_token_id):
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
        try:
            self.cur.execute("""
                INSERT INTO Products (name, category, co2Emission, nftID)
                VALUES (?, ?, ?, ?)""",
                (name, category, co2Emission, nft_token_id))
            self.conn.commit()
            return 0
        except sqlite3.IntegrityError:
            return -1

    def update_product(self, product_id, co2Emission=None):
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
        try:
            query = "UPDATE Products SET "
            params = []

            if co2Emission is not None:
                query += "co2Emission = ?, "
                params.append(co2Emission)

            # Rimuove la virgola finale e aggiunge la WHERE
            query = query.rstrip(", ") + " WHERE nftID = ?"
            params.append(product_id)

            self.cur.execute(query, params)
            self.conn.commit()

            if self.cur.rowcount > 0:
                print(Fore.GREEN + "Product emissions updated successfully!\n" + Style.RESET_ALL)
                return 0
            else:
                print(Fore.YELLOW + "No records updated (ID not found or no changes made).\n" + Style.RESET_ALL)
                return -1

        except sqlite3.Error as e:
            print(Fore.RED + f"Error updating product: {e}" + Style.RESET_ALL)
            return -1

# ---------- END PRODUCTS ----------

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
        try:
            self.cur.execute("""
                INSERT INTO Transactions (username_from, username_to, amount, type, tx_hash)
                VALUES (?, ?, ?, ?, ?)
                """, (username_from, username_to, amount, type, tx_hash))
            self.conn.commit()
            return 0
        except sqlite3.IntegrityError:
            return -1

    def get_user_transactions(self, user_username):
        """
        Retrieves all transactions involving a specific user, either as sender or receiver.

        Args:
            user_username (str): The username of the user whose transactions are to be retrieved.

        Returns:
            list of Transaction: A list of Transaction objects ordered by timestamp descending.
        """
        self.cur.execute("""
                            SELECT * FROM Transactions
                            WHERE username_from = ? OR username_to = ?
                            ORDER BY timestamp DESC
                            """, (user_username, user_username))
        transactions = [Transaction(id, username_from, username_to, amount, type, tx_hash, timestamp)
                        for id, username_from, username_to, amount, type, tx_hash, timestamp in self.cur.fetchall()]

        return transactions

# ---------- TRANSACTIONS ----------

# ---------- END TRANSACTIONS ----------

    def encrypt_private_k(self, private_key, passwd):
        passwd_hash = hashlib.sha256(passwd.encode('utf-8')).digest()
        key = base64.urlsafe_b64encode(passwd_hash)
        cipher_suite = Fernet(key)
        return cipher_suite.encrypt(private_key.encode('utf-8'))

    def decrypt_private_k(self, encrypted_private_k, passwd):
        passwd_hash = hashlib.sha256(passwd.encode('utf-8')).digest()
        key = base64.urlsafe_b64encode(passwd_hash)
        cipher_suite = Fernet(key)
        return cipher_suite.decrypt(encrypted_private_k).decode('utf-8')

    def hash_function(self, password):
        salt = os.urandom(16)
        digest = hashlib.scrypt(password.encode(), salt=salt, n=2, r=8, p=1, dklen=64)
        return f"{digest.hex()}${salt.hex()}"



