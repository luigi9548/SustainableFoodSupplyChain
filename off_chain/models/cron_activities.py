from models.model_base import Model
from colorama import Fore, Style, init
from models.model_base import Model

class Cron_Activities(Model):
    """
    This class defines the Cron_Activities model, which tracks detailed records of activities,  
    extending the functionality provided by the Model class.
    """
    def __init__(self, id, description, update_datetime, creation_datetime, accepted, activity_id, co2_reduction, db):
        """
        Initializes a new instance of the Cron_Activities class, representing a specific record of an activity  
        performed by a credentialed user.

        Parameters:
        - id: Unique identifier for the Cron_Activities record  
        - description: A detailed description of the activity  
        - credential_id: The ID of the credentialed user who performed the activity  
        - update_datetime: The timestamp when the activity record was last updated  
        - creation_datetime: The timestamp when the activity record was created  
        - accepted: Boolean indicating whether the activity was accepted  
        - activity_id: The ID of the activity associated with the record  
        - co2_reduction: The amount of CO2 reduced by the activity  
        """
        super().__init__()
        self.id = id
        self.description = description
        self.update_datetime = update_datetime
        self.creation_datetime = creation_datetime
        self.accepted = accepted
        self.activity_id = activity_id
        self.co2_reduction = co2_reduction
        self.db = db

    # Getter methods for each attribute
    def get_id(self):
        return self.id

    def get_description(self):
        return self.description

    def get_update_datetime(self):
        return self.update_datetime

    def get_creation_datetime(self):
        return self.creation_datetime

    def get_accepted(self):
        return self.accepted

    def get_activity_id(self):
        return self.activity_id

    def get_co2_reduction(self):
        return self.co2_reduction

    def save(self):
        """
        Saves a new or updates an existing Cron_Activities record in the database.
        Implements SQL queries to insert or update credentials based on the presence of an ID.
        """
        if self.id is None:
            # Inserts new cron_activities record into the database
            result = self.db.register_cron_activity(self.description, self.accepted, self.activity_id, self.co2_reduction)
            if result == 0:
                self.id = self.cur.lastrowid
        else:
            # Updates existing cron_activities record in the database
            result = self.db.update_cron_activity(self.id, self.description, self.accepted, self.activity_id, self.co2_reduction)
        if result == 0:
            print(Fore.GREEN + 'Information saved correctly!\n' + Style.RESET_ALL)
        else:
            print(Fore.RED + 'Error saving information!\n' + Style.RESET_ALL)
        return result

    def delete(self):
        """
        Deletes a Cron_Activities record from the database based on its ID.
        """
        if self.id is not None:
            result = self.db.delete_cron_activity(self.id)
            if result == 0:
                print(Fore.GREEN + 'Information deleted correctly!\n' + Style.RESET_ALL)
            else:
                print(Fore.RED + 'Error deleting information!\n' + Style.RESET_ALL)
            return result
        else:
            return -1
