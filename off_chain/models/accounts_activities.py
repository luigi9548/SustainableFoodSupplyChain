from models.model_base import Model

class Accounts_Activities(Model):
    """
    This class defines the Accounts_Activities model, which establishes a relationship between user accounts and 
    the activities they are associated with, extending the functionality provided by the Model class.
    """
    def __init__(self, account_id, activity_id):
        """
        Initializes a new instance of the Accounts_Activities class, linking a specific account to an activity.

        Parameters:
        - account_id: The unique identifier of the account  
        - activity_id: The unique identifier of the activity associated with the account  
        """
        super().__init__()
        self.account_id = account_id
        self.activity_id = activity_id

    # Getter methods for each attribute
    def get_account_id(self):
        return self.account_id

    def get_activity_id(self):
        return self.activity_id

    def save(self):
        """
        Saves a new or updates an existing Credentials record in the database.
        Implements SQL queries to insert or update credentials based on the presence of an ID.
        """
        if self.id is None:
             # Insert new aaccount_activities record
             self.cur.execute('''INSERT INTO Accounts_Activities (account_id, activity_id)
                                 VALUES (?, ?)''', #Question marks as placeholders are used to prevent SQL Injection attacks
                              (self.account_id, self.activity_id))
             self.id = self.cur.lastrowid # Update the ID with the last row inserted ID if new record
        else:
             # Update existing account_activities record
             self.cur.execute('''UPDATE Accounts_Activities SET account_id=?, activity_id=?
                                 WHERE id=?''',
                              (self.account_id, self.activity_id, self.id))
        self.conn.commit()

    def delete(self):
        """
        Deletes an existing account_activities record from the database.
        """
        self.cur.execute('''DELETE FROM Accounts_Activities WHERE id=?''', (self.id,))
        self.conn.commit()