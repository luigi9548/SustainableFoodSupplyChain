from models.model_base import Model
from colorama import Fore, Style, init
from db.db_operations import DatabaseOperations

class Activities(Model):
    """
    This class defines the Activities model, which stores information about different types of activities,  
    extending the functionality provided by the Model class.
    """

    def __init__(self, id, type, description, db):
        """
        Initializes a new instance of the Activity class, representing a specific action or investment.

        Parameters:
        - id: Unique identifier for the activity record  
        - type: The category of activity ('investment in a project for reduction', 'performing an action')  
        - description: An explanation of the activity  

        """
        super().__init__()
        self.id = id
        self.type = type
        self.description = description
        self.db = db

    # Getter methods for each attribute
    def get_id(self):
        return self.id

    def get_type(self):
        return self.type

    def get_description(self):
        return self.description

    def save(self):
        """
        Saves a new or updates an existing Activities record in the database.
        Implements SQL queries to insert or update credentials based on the presence of an ID.
        """
        if self.id is None:
            # Insert new activities record
            result = self.db.register_activities(self.type, self.description)
            if result == 0:
                self.id = self.cur.lastrowid # Update the ID with the last row inserted ID if new record
        else:
            # Update existing activities record
            result = self.db.update_activities(self.id, self.type, self.description)
        if result == 0:
            print(Fore.GREEN + 'Information saved correctly!\n' + Style.RESET_ALL)
        else:
            print(Fore.RED + 'Error saving information!\n' + Style.RESET_ALL)
        return result

    def delete(self):
        """
        Deletes an existing Activities record from the database.
        """
        if self.id is not None:
            result = self.db.delete_activities(self.id)
            if result == 0:
                print(Fore.GREEN + 'Information deleted correctly!\n' + Style.RESET_ALL)
            else:
                print(Fore.RED + 'Error deleting information!\n' + Style.RESET_ALL)
            return result
        else:
            return -1
