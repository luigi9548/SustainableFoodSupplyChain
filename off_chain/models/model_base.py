import sqlite3
from config import config

class Model:
    """Base model to be extended for implementing other models."""
    
    def __init__(self):
        """Constructor that initializes the database connection."""
        self.conn = sqlite3.connect(config.config["db_path"])
        self.cur = self.conn.cursor()
    
    def __del__(self):
        """Destructor that closes the database connection."""
        self.conn.close()


