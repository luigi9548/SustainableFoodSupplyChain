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
        self.cur.execute("DROP TABLE IF EXISTS Credentials")
        self.cur.execute("DROP TABLE IF EXISTS Accounts")
        self.cur.execute("DROP TABLE IF EXISTS Activities")
        self.cur.execute("DROP TABLE IF EXISTS Accounts_Activities")
        self.cur.execute("DROP TABLE IF EXISTS Cron_Activities")
        self.cur.execute("DROP TABLE IF EXISTS Licences")
        self.cur.execute("DROP TABLE IF EXISTS Products")

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
                        harvestDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        sensorId INTEGER NOT NULL
                        );''')
        self.conn.commit()

    def insert_test_records(self):
        self.cur.execute('''INSERT INTO Licences (type, licence_number) VALUES
                            ('FARMER', '2001'),
                            ('CARRIER', '2002'),
                            ('SELLER', '2003'),
                            ('PRODUCER', '2004'),
                            ('CERTIFIER', '2005');''')

        self.cur.execute('''INSERT INTO Credentials (username, password, public_key, private_key) VALUES
                            ('farmer_user', 'N5K+n8DAAmZKfbqK', '0xd141E7900D4f756f492e463957BC0e68202CbD81', '0x30c4e61c6f0e1803219ecdccdf576086f8f4e128d1911f68db95d05fd5fb5a49'),
                            ('carrier_user', 'd3bHfBVNydAh+5yy', '0x939878DE3937a84c413Dc4ADE09440c00F151911', '0x164f9c762d3cec7ba488e8488e5052abd413c5418db1197719ad00f9a4d76a00');''')

        self.cur.execute('''INSERT INTO Accounts (username, type, name, licence_id, lastname, birthday, birth_place, residence, phone, mail) VALUES
                            ('farmer_user', 'FARMER', 'John', 1, 'Doe', '1980-05-10', 'Milan', 'Rome', '1234567890', 'john@example.com'),
                            ('carrier_user', 'CARRIER', 'Jane', 2, 'Smith', '1985-08-20', 'Paris', 'London', '0987654321', 'jane@example.com');''')

        self.cur.execute('''INSERT INTO Activities (type, description) VALUES
                            ('investment in a project for reduction', 'Investing in solar panels'),
                            ('performing an action', 'Using electric vehicles for transport');''')

        self.cur.execute('''INSERT INTO Accounts_Activities (username, activity_id) VALUES
                            ('farmer_user', 1),
                            ('carrier_user', 2);''')

        self.cur.execute('''INSERT INTO Cron_Activities (description, username, state, activity_id, co2_reduction) VALUES
                            ('Solar panel investment', 'farmer_user', 0, 1, 50.0),
                            ('Electric vehicle implementation', 'carrier_user', 0, 2, 30.5);''')

        self.cur.execute('''INSERT INTO Products (name, category, co2Emission, sensorId) VALUES
                            ('Apple', 'FRUIT', 10, 101),
                            ('Beef', 'MEAT', 50, 102),
                            ('Cheese', 'DAIRY', 20, 103);''')

        self.conn.commit()

    def register_creds(self, username, password, role, public_key, private_key, temp_code=None, temp_code_validity=None):
        try:
            if self.check_username(username) == 0:
                obfuscated_private_k = self.encrypt_private_k(private_key, password)
                hashed_passwd = self.hash_function(password)
                self.cur.execute("""
                    INSERT INTO Credentials (username, password, role, public_key, private_key, temp_code, temp_code_validity)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (username, hashed_passwd, role, public_key, obfuscated_private_k, temp_code, temp_code_validity))
                self.conn.commit()
                return 0
            else:
                return -1
        except sqlite3.IntegrityError as e:
            print(Fore.RED + f'Internal error: {e}' + Style.RESET_ALL) #possiamo anche non stampare e??? boh -> rientra nella mitigazione del misuso secondo me stamperei
            return -1
        
    def update_creds(self, id, username=None, password=None, role=None, public_key=None, private_key=None, temp_code=None, temp_code_validity=None):
        """
        Updates an existing credentials record in the database.
        Only updates fields that are provided (non-None).
        """
        try:
            query = "UPDATE Credentials SET "
            params = []
            
            if username:
                query += "username = ?, "
                params.append(username)
            
            if password:
                hashed_passwd = self.hash_function(password)
                query += "password = ?, "
                params.append(hashed_passwd)
            
            if role:
                query += "role = ?, "
                params.append(role)
            
            if public_key:
                query += "public_key = ?, "
                params.append(public_key)
            
            if private_key:
                obfuscated_private_k = self.encrypt_private_k(private_key, password if password else self.get_current_password(id))
                query += "private_key = ?, "
                params.append(obfuscated_private_k)
            
            if temp_code is not None:
                query += "temp_code = ?, "
                params.append(temp_code)
            
            if temp_code_validity is not None:
                query += "temp_code_validity = ?, "
                params.append(temp_code_validity)
            
            # Remove trailing comma and space
            query = query.rstrip(", ") + " WHERE id = ?"
            params.append(id)
            
            self.cur.execute(query, params)
            self.conn.commit()
            
            if self.cur.rowcount > 0:
                print(Fore.GREEN + "Information updated correctly!\n" + Style.RESET_ALL)
                return 0
            else:
                print(Fore.YELLOW + "No records updated (ID not found or no changes made).\n" + Style.RESET_ALL)
                return -1

        except sqlite3.Error as e:
            print(Fore.RED + f'Error updating credentials: {e}' + Style.RESET_ALL)
            return -1

    def delete_creds(self, id):
        """
        Deletes a credentials record from the database based on its ID.
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

    def check_username(self, username):
        self.cur.execute("SELECT COUNT(*) FROM Credentials WHERE username = ?", (username,))
        return -1 if self.cur.fetchone()[0] > 0 else 0

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

    def check_valid_licence(self, role, licence_number):
        """
        Checks if a valid licence exists for a given role.
        """
        self.cur.execute("SELECT COUNT(*) FROM Licences WHERE type = ? AND licence_number = ?", (role, licence_number))
        return self.cur.fetchone()[0] > 0
    
    def register_licences(self, type, licence_number):
        """
        Registers a new licence in the database.
        """
        try:
            self.cur.execute("""
                INSERT INTO Licences (type, licence_number)
                VALUES (?, ?)""",
                (type, licence_number)
            )
            self.conn.commit()
            return 0  # Success
        except sqlite3.IntegrityError as e:
            print(Fore.RED + f'Error inserting licence: {e}' + Style.RESET_ALL)
            return -1  # Error

    def update_licences(self, id, type=None, licence_number=None):
        """
        Updates an existing licence record.
        Only updates fields that are provided (non-None).
        """
        try:
            query = "UPDATE Licences SET "
            params = []
            
            if type is not None:
                query += "type = ?, "
                params.append(type)
            
            if licence_number is not None:
                query += "licence_number = ?, "
                params.append(licence_number)

            # Always update the timestamp
            query += "update_datetime = CURRENT_TIMESTAMP, "

            # Remove the last comma
            query = query.rstrip(", ") + " WHERE id = ?"
            params.append(id)

            self.cur.execute(query, params)
            self.conn.commit()

            if self.cur.rowcount > 0:
                print(Fore.GREEN + "Licence updated successfully!\n" + Style.RESET_ALL)
                return 0
            else:
                print(Fore.YELLOW + "No records updated (ID not found or no changes made).\n" + Style.RESET_ALL)
                return -1

        except sqlite3.Error as e:
            print(Fore.RED + f'Error updating licence: {e}' + Style.RESET_ALL)
            return -1

    def delete_licences(self, id):
        """
        Deletes a licence record from the database based on its ID.
        """
        try:
            self.cur.execute("DELETE FROM Licences WHERE id = ?", (id,))
            self.conn.commit()

            if self.cur.rowcount > 0:
                print(Fore.GREEN + "Licence deleted successfully!\n" + Style.RESET_ALL)
                return 0
            else:
                print(Fore.YELLOW + "No record found with the given ID.\n" + Style.RESET_ALL)
                return -1

        except sqlite3.Error as e:
            print(Fore.RED + f'Error deleting licence: {e}' + Style.RESET_ALL)
            return -1

    def get_credentials(self):
        self.cur.execute("SELECT * FROM Credentials")
        return self.cur.fetchall()

    def get_accounts(self):
        self.cur.execute("SELECT * FROM Accounts")
        return self.cur.fetchall()

    def get_activities(self):
        self.cur.execute("SELECT * FROM Activities")
        return self.cur.fetchall()

    def get_accounts_activities(self):
        self.cur.execute("SELECT * FROM Accounts_Activities")
        return self.cur.fetchall()

    def get_cron_activities(self):
        self.cur.execute("SELECT * FROM Cron_Activities")
        return self.cur.fetchall()

    def get_products(self):
        self.cur.execute("SELECT * FROM Products")
        return self.cur.fetchall()

    def update_account(self, username, name, lastname, birthday, birth_place, residence, phone, mail, id):
        """
        Updates an existing account record in the database.
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

    def delete_account(self, id):
        """
        Deletes an account record from the database.
        """
        try:
           self.cur.execute("DELETE FROM Accounts WHERE id = ?", (id,))
           self.conn.commit()
           return 0
        except sqlite3.Error:
           return -1

    def register_account_activities(self, account_id, activity_id):
        """
          Inserts a new account-activity association.
        """
        try:
          self.cur.execute("INSERT INTO Accounts_Activities (account_id, activity_id) VALUES (?, ?)", 
                         (account_id, activity_id))
          self.conn.commit()
          return 0
        except sqlite3.IntegrityError:
          return -1
        
    
    def update_account_activities(self, record_id, account_id, activity_id):
        """
        Updates an existing account-activity association.
        """
        try:
            self.cur.execute("UPDATE Accounts_Activities SET account_id = ?, activity_id = ? WHERE id = ?", 
                         (account_id, activity_id, record_id))
            self.conn.commit()
            return 0
        except sqlite3.IntegrityError:
            return -1
        
    def delete_account_activities(self, record_id):
        """
        Deletes an account-activity association.
        """
        try:
            self.cur.execute("DELETE FROM Accounts_Activities WHERE id = ?", (record_id,))
            self.conn.commit()
            return 0
        except sqlite3.IntegrityError:
            return -1

    def register_activities(self, type, description):
        """
        Inserts a new activity record into the database.
        """
        try:
           self.cur.execute("""
            INSERT INTO Activities (type, description) 
            VALUES (?, ?)""", 
            (type, description))
           self.conn.commit()
           return 0
        except sqlite3.IntegrityError:
           return -1

    def update_activities(self, id, type, description):
        """
         Updates an existing activity record in the database.
        """
        try:
           self.cur.execute("""
            UPDATE Activities 
            SET type = ?, description = ? 
            WHERE id = ?""",
            (type, description, id))
           self.conn.commit()
           return 0
        except sqlite3.Error:
           return -1

    def delete_activities(self, id):
        """
        Deletes an activity record from the database.
        """
        try:
           self.cur.execute("DELETE FROM Activities WHERE id = ?", (id,))
           self.conn.commit()
           return 0
        except sqlite3.Error:
           return -1
   

    def register_cron_activity(self, description, accepted, activity_id, co2_reduction):
        """
        Registers a new cron activity in the database.
        """
        try:
            self.cur.execute("""
                INSERT INTO Cron_Activities (description, accepted, activity_id, co2_reduction, update_datetime, creation_datetime)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
                (description, accepted, activity_id, co2_reduction)
            )
            self.conn.commit()
            return 0  # Success
        except sqlite3.IntegrityError as e:
            print(Fore.RED + f'Error inserting cron activity: {e}' + Style.RESET_ALL)
            return -1  # Error

    def update_cron_activity(self, id, description=None, accepted=None, activity_id=None, co2_reduction=None):
        """
        Updates an existing cron activity record.
        Only updates fields that are provided (non-None).
        """
        try:
            query = "UPDATE Cron_Activities SET "
            params = []
            
            if description is not None:
                query += "description = ?, "
                params.append(description)
            
            if accepted is not None:
                query += "accepted = ?, "
                params.append(accepted)
            
            if activity_id is not None:
                query += "activity_id = ?, "
                params.append(activity_id)
            
            if co2_reduction is not None:
                query += "co2_reduction = ?, "
                params.append(co2_reduction)

            # Always update the timestamp
            query += "update_datetime = CURRENT_TIMESTAMP, "

            # Remove the last comma
            query = query.rstrip(", ") + " WHERE id = ?"
            params.append(id)

            self.cur.execute(query, params)
            self.conn.commit()

            if self.cur.rowcount > 0:
                print(Fore.GREEN + "Cron activity updated successfully!\n" + Style.RESET_ALL)
                return 0
            else:
                print(Fore.YELLOW + "No records updated (ID not found or no changes made).\n" + Style.RESET_ALL)
                return -1

        except sqlite3.Error as e:
            print(Fore.RED + f'Error updating cron activity: {e}' + Style.RESET_ALL)
            return -1

    def delete_cron_activity(self, id):
        """
        Deletes a cron activity record from the database based on its ID.
        """
        try:
            self.cur.execute("DELETE FROM Cron_Activities WHERE id = ?", (id,))
            self.conn.commit()

            if self.cur.rowcount > 0:
                print(Fore.GREEN + "Cron activity deleted successfully!\n" + Style.RESET_ALL)
                return 0
            else:
                print(Fore.YELLOW + "No record found with the given ID.\n" + Style.RESET_ALL)
                return -1

        except sqlite3.Error as e:
            print(Fore.RED + f'Error deleting cron activity: {e}' + Style.RESET_ALL)
            return -1

    def insert_product(self, name, category, co2Emission, sensorId):
        try:
            self.cur.execute("""
                INSERT INTO Products (name, category, co2Emission, harvestDate, sensorId)
                VALUES (?, ?, ?, ?, ?)""",
                (name, category, co2Emission, self.today_date, sensorId))
            self.conn.commit()
            return 0
        except sqlite3.IntegrityError:
            return -1

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

    def check_credentials(self, username, password):
        result = self.cur.execute("SELECT password FROM Credentials WHERE username = ?", (username,)).fetchone()
        if result:
            saved_hash = result[0]
            params = saved_hash.split('$')
            hashed_passwd = hashlib.scrypt(password.encode(), salt=bytes.fromhex(params[1]), n=2, r=8, p=1, dklen=64)
            return hashed_passwd.hex() == params[0]
        return False

    def change_password(self, username, old_pass, new_pass):
        if self.check_credentials(username, old_pass):
            new_hash = self.hash_function(new_pass)
            try:
                self.cur.execute("UPDATE Credentials SET password = ? WHERE username = ?", (new_hash, username))
                self.conn.commit()
                return 0
            except Exception:
                return -1
        return -1

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