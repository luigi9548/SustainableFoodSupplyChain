from models.model_base import Model

class Licences(Model):
    """
    This class defines the Licence model, which associates a licence ID with a specific account type,  
    extending the functionality provided by the Model class.
    """

    def __init__(self, id, type, licence_number):
        """
        Initializes a new instance of the Licence class, associating a licence ID with an account type.

        Parameters:
        - id: Unique identifier for the licence record  
        - type: The category of licence ('FARMER', 'CARRIER', 'SELLER', 'PRODUCER', 'CERTIFIER')  
        - licence_number: A unique identifier assigned to the licence  
        """
        super().__init__()
        self.id = id
        self.type = type
        self.licence_number = licence_number

    # Getter method for each attribute
    def get_id(self):
        return self.id

    def get_type(self):
        return self.type

    def get_licence_number(self):
        return self.licence_number

    def save(self):
        """
        Saves a new or updates an existing Licences record in the database.
        Implements SQL queries to insert or update licences based on the presence of an ID.
        """
        if self.id is None:
            # Insert new licences record
            self.cur.execute('''INSERT INTO Licences (type, licence_number) 
                                VALUES (?, ?)''', #Question marks as placeholders are used to prevent SQL Injection attacks
                             (self.type, self.licence_number))
            self.id = self.cur.lastrowid # Update the ID with the last row inserted ID if new record
        else:
            # Update existing licences record
            self.cur.execute('''UPDATE Licences SET type=?, licence_number=? 
                                WHERE id=?''', 
                             (self.type, self.licence_number, self.id))
        self.conn.commit()

    def delete(self):
        """
        Deletes a Lincences record from the database based on its ID.
        """
        if self.id is not None:
            self.cur.execute('DELETE FROM Licences WHERE id=?', (self.id,))
            self.conn.commit()

