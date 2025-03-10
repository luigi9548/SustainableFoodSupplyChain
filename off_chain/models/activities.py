from models.model_base import Model

class Activities(Model):
    """
    This class defines the Activities model, which stores information about different types of activities,  
    extending the functionality provided by the Model class.
    """

    def __init__(self, id, type, description):
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
            self.cur.execute('''INSERT INTO Activities (type, description)
                                VALUES (?, ?)''', #Question marks as placeholders are used to prevent SQL Injection attacks
                             (self.type, self.description))
            self.id = self.cur.lastrowid # Update the ID with the last row inserted ID if new record
        else:
            # Update existing activities record
            self.cur.execute('''UPDATE Activities SET type=?, description=? WHERE id=?''',
                                (self.type, self.description, self.id))     
        self.conn.commit()

    def delete(self):
        """
        Deletes an existing Activities record from the database.
        """
        self.cur.execute('''DELETE FROM Activities WHERE id=?''', (self.id,))
        self.conn.commit()
