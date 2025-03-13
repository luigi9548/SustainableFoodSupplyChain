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

    def check_username(self, username):
        self.cur.execute("SELECT COUNT(*) FROM Credentials WHERE username = ?", (username,))
        return -1 if self.cur.fetchone()[0] > 0 else 0
    

    def check_valid_licence(self, role, licence_number):
        """
        Checks if a valid licence exists for a given role.
        """
        self.cur.execute("SELECT COUNT(*) FROM Licences WHERE type = ? AND licence_number = ?", (role, licence_number))
        return self.cur.fetchone()[0] > 0

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

    def insert_account(self, credential_id, type, name, lastname, birthday, birth_place, residence, phone, mail, licence_id):
        try:
            self.cur.execute("""
                INSERT INTO Accounts (credential_id, type, name, lastname, birthday, birth_place, residence, phone, mail, licence_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (credential_id, type, name, lastname, birthday, birth_place, residence, phone, mail, licence_id))
            self.conn.commit()
            return 0
        except sqlite3.IntegrityError:
            return -1

    def insert_activity(self, type, description):
        try:
            self.cur.execute("INSERT INTO Activities (type, description) VALUES (?, ?)", (type, description))
            self.conn.commit()
            return 0
        except sqlite3.IntegrityError:
            return -1

    def assign_activity_to_account(self, account_id, activity_id):
        try:
            self.cur.execute("INSERT INTO Accounts_Activities (account_id, activity_id) VALUES (?, ?)", (account_id, activity_id))
            self.conn.commit()
            return 0
        except sqlite3.IntegrityError:
            return -1

    def insert_cron_activity(self, description, credential_id, accepted, activity_id, co2_reduction):
        try:
            self.cur.execute("""
                INSERT INTO Cron_Activities (description, credential_id, accepted, activity_id, co2_reduction, creation_datetime)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (description, credential_id, accepted, activity_id, co2_reduction, self.today_date))
            self.conn.commit()
            return 0
        except sqlite3.IntegrityError:
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