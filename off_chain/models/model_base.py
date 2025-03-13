import sqlite3
from config import config

class Model:
    """Base model to be extended for implementing other models."""
    
    def save(self):
        """Virtual method to save the model. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement this method.")
    
    def delete(self):
        """Virtual method to delete the model. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement this method.")


