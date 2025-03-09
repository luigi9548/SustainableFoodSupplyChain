import sqlite3
from config import config

class Model:
    """Base model to be extended for implementing other models."""
    
    def __init__(self):
        """Constructor that initializes the database connection."""
        self.conn = sqlite3.connect(config["db_path"])
        self.cur = self.conn.cursor()
    
    def save(self):
        """Virtual method to save the model. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement this method.")
    
    def delete(self):
        """Virtual method to delete the model. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement this method.")
    
    def close_connection(self):
        """Closes the database connection explicitly."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        """Destructor that closes the database connection."""
        self.close_connection()

