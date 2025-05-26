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


cur.execute('''CREATE TABLE Accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            type TEXT CHECK(type IN ('FARMER', 'CARRIER', 'SELLER', 'PRODUCER', 'CERTIFIER')) NOT NULL,
            name TEXT NOT NULL,
            lastname TEXT NOT NULL,
            birthday TEXT NOT NULL,
            birth_place TEXT,
            residence TEXT,
            phone TEXT,
            mail TEXT,
            FOREIGN KEY (username) REFERENCES Credentials(username)
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

cur.execute('''CREATE TABLE Transactions (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               username_from TEXT,
               username_to TEXT,
               amount INTEGER NOT NULL,
               type TEXT CHECK(type IN ('MINT', 'BURN', 'TRANSFER')) NOT NULL,
               tx_hash TEXT,
               timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
               );
               ''')

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
            nftID INTEGER NOT NULL,
            harvestDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            update_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );''')

# trigger for automatic update of update_datetime
cur.execute('''CREATE TRIGGER IF NOT EXISTS update_Products_timestamp
                        AFTER UPDATE ON Products
                        FOR EACH ROW
                        BEGIN
                        UPDATE Products SET update_datetime = CURRENT_TIMESTAMP WHERE id = OLD.id;
                        END;''')



con.commit()
con.close()
