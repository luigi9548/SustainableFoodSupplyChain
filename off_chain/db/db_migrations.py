import random
import sqlite3
import string
from config import config

con = sqlite3.connect(config["db_path"])
cur = con.cursor()


cur.execute("DROP TABLE IF EXISTS Credentials")
cur.execute("DROP TABLE IF EXISTS Accounts")
cur.execute("DROP TABLE IF EXISTS Activities")
cur.execute("DROP TABLE IF EXISTS Accounts_Activities")
cur.execute("DROP TABLE IF EXISTS Cron_Activities")
cur.execute("DROP TABLE IF EXISTS Licences")

# TODO do we want to leave the admin?
# TODO public, private key, encrypt at rest.
cur.execute('''CREATE TABLE Credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT CHECK(role IN ('USER_CERTIFIER', 'USER_ACTOR', 'ADMIN')) NOT NULL,
            public_key TEXT NOT NULL,
            private_key TEXT NOT NULL,
            temp_code TEXT,
            temp_code_validity DATETIME,
            publicKey TEXT NOT NULL,
            privateKey TEXT NOT NULL,
            update_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            creation_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );''')

# licence it's mandatory for each actor
cur.execute('''CREATE TABLE Accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credential_id INTEGER NOT NULL,
            type TEXT CHECK(type IN ('FARMER', 'CARRIER', 'SELLER', 'PRODUCER', 'CERTIFIER')) NOT NULL,
            name TEXT NOT NULL,
            licence_id INTEGER NOT NULL,
            lastname TEXT NOT NULL,
            birthday TEXT NOT NULL,
            birth_place TEXT,
            residence TEXT,
            phone TEXT,
            mail TEXT,
            FOREIGN KEY (credential_id) REFERENCES Credentials(id),
            FOREIGN KEY (licence_id) REFERENCES Licences(id)
            );''')

# Licences table to verufy the authenticity of role and mitigate misuese (aggiorno io le tabelle sul misuso, in fase di inserimento utente verifichiamo al sua licenza)
cur.execute('''CREATE TABLE Licences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT CHECK(type IN ('FARMER', 'CARRIER', 'SELLER', 'PRODUCER', 'CERTIFIER')) NOT NULL,
            licence_number TEXT NOT NULL UNIQUE
            );''')


cur.execute('''CREATE TABLE Activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT CHECK(type IN ('investment in a project for reduction', 'performing an action')) NOT NULL,
            description TEXT NOT NULL
            );''')


cur.execute('''CREATE TABLE Accounts_Activities (
            account_id INTEGER NOT NULL,
            activity_id INTEGER NOT NULL,
            PRIMARY KEY (account_id, activity_id),
            FOREIGN KEY (account_id) REFERENCES Accounts(id),
            FOREIGN KEY (activity_id) REFERENCES Activities(id)
            );''')


cur.execute('''CREATE TABLE Cron_Activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            credential_id INTEGER NOT NULL,
            update_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            creation_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            accepted BOOLEAN NOT NULL,
            activity_id INTEGER NOT NULL,
            co2_reduction DECIMAL NOT NULL,
            FOREIGN KEY (credential_id) REFERENCES Credentials(id),
            FOREIGN KEY (activity_id) REFERENCES Activities(id)
            );''')

cur.execute('''CREATE TABLE Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT CHECK(role IN ('FRUIT', 'MEAT', 'DAIRY')) NOT NULL,
            co2Emission INTEGER NOT NULL,
            harvestDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            sensorId INTEGER NOT NULL
            );''')

# Inserting 10 random licences for each role except 'CERTIFICATORE'
# (per mitigare disuso e abuso verranne inviate via mail le licenze ad ogni certificatore, mi occupo io della cosa e di correggere la relazione)
def generate_random_licence():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

roles = ['FARMER', 'CARRIER', 'SELLER', 'PRODUCER']
for role in roles:
    for _ in range(10):
        licence_number = generate_random_licence()
        cur.execute("INSERT INTO Licences (type, licence_number) VALUES (?, ?)", (role, licence_number))

con.commit()
con.close()
