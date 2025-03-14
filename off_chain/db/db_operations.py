import datetime
import sqlite3
import os
import hashlib
import base64
from cryptography.fernet import Fernet
from colorama import Fore, Style, init
from config import config

class DatabaseOperations:
    """
    Handles all interactions with the database for user data manipulation and retrieval.
    """
    init(convert=True)

    def __init__(self):
        self.conn = sqlite3.connect(config["db_path"])
        self.cur = self.conn.cursor()
        self.today_date = datetime.date.today().strftime('%Y-%m-%d')

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

    def check_username(self, username):
        self.cur.execute("SELECT COUNT(*) FROM Credentials WHERE username = ?", (username,))
        return -1 if self.cur.fetchone()[0] > 0 else 0
    

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

    def register_account(self, credential_id, type, name, lastname, birthday, birth_place, residence, phone, mail, licence_id):
        """
        Inserts a new account record into the database.
        """
        try:
            self.cur.execute("""
            INSERT INTO Accounts (credential_id, type, name, lastname, birthday, birth_place, residence, phone, mail, licence_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (credential_id, type, name, lastname, birthday, birth_place, residence, phone, mail, licence_id))
            self.conn.commit()
            return 0
        except sqlite3.IntegrityError:
            return -1

    def update_account(self, credential_id, type, name, licence_id, lastname, birthday, birth_place, residence, phone, mail, id):
        """
        Updates an existing account record in the database.
        """
        try:
            self.cur.execute("""
            UPDATE Accounts 
            SET credential_id = ?, type = ?, name = ?, licence_id = ?, lastname = ?, birthday = ?, 
                birth_place = ?, residence = ?, phone = ?, mail = ? 
            WHERE id = ?""",
            (credential_id, type, name, licence_id, lastname, birthday, birth_place, residence, phone, mail, id))
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