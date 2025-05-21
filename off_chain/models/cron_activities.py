from colorama import Fore, Style, init
from models.model_base import Model

class Cron_Activities(Model):
    """
    This class defines the Cron_Activities model, which tracks detailed records of activities,  
    extending the functionality provided by the Model class.
    """
    def __init__(self, id, description, username, update_datetime, creation_datetime, state, activity_id, co2_reduction):
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
        self.username = username
        self.update_datetime = update_datetime
        self.creation_datetime = creation_datetime
        self.state = state
        self.activity_id = activity_id
        self.co2_reduction = co2_reduction

    # Getter methods for each attribute
    def get_id(self):
        return self.id

    def get_username(self):
        return self.username

    def get_description(self):
        return self.description

    def get_update_datetime(self):
        return self.update_datetime

    def get_creation_datetime(self):
        return self.creation_datetime

    def get_state(self):
        return self.state

    def get_activity_id(self):
        return self.activity_id

    def get_co2_reduction(self):
        return self.co2_reduction