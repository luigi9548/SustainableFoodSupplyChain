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
cur.execute("DROP TABLE IF EXISTS Products")

# TODO do we want to leave the admin?
# TODO public, private key, encrypt at rest.
cur.execute('''CREATE TABLE IF NOT EXISTS Credentials (
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
cur.execute('''CREATE TRIGGER update_Credentials_timestamp
            AFTER UPDATE ON Credentials
            FOR EACH ROW
            BEGIN
            UPDATE Credentials SET update_datetime = CURRENT_TIMESTAMP WHERE id = OLD.id;
            END;''')

# licence it's mandatory for each actor
cur.execute('''CREATE TABLE Accounts (
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


cur.execute('''CREATE TABLE IF NOT EXISTS Accounts_Activities (
               username TEXT NOT NULL,
               activity_id INTEGER NOT NULL,
               PRIMARY KEY (username, activity_id),
               FOREIGN KEY (username) REFERENCES Credentials(username),
               FOREIGN KEY (activity_id) REFERENCES Activities(id)
               );''')


cur.execute('''CREATE TABLE IF NOT EXISTS Cron_Activities (
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

cur.execute('''CREATE TRIGGER update_Cron_Activities_timestamp
            AFTER UPDATE ON Cron_Activities
            FOR EACH ROW
            BEGIN
            UPDATE Cron_Activities SET update_datetime = CURRENT_TIMESTAMP WHERE id = OLD.id;
            END;''')

cur.execute('''CREATE TABLE Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT CHECK(category IN ('FRUIT', 'MEAT', 'DAIRY')) NOT NULL,
            co2Emission INTEGER NOT NULL,
            harvestDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
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
