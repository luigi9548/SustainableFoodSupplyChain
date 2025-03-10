from models.model_base import Model

class Credentials(Model):
    """
    This class defines the Credentials model, which stores user authentication and authorization details,
    extending the functionality provided by the Model class.
    """

    def __init__(self, id, username, password, role, public_key, private_key, temp_code, temp_code_validity, publicKey, privateKey, update_datetime, creation_datetime):       
        """
        Initializes a new instance of Credentials class with the provided user credentials details.

        Parameters:
        - id: Unique identifier for the credentials record
        - username: Username associated with the credentials
        - password: Password for user authentication
        - role: The role assigned to the user ('USER_CERTIFIER', 'USER_ACTOR', 'ADMIN')
        - public_key: ...
        - private_key: ...
        - temp_code: Temporary code for two-factor authentication (optional)
        - temp_code_validity: Expiration  date/time for the temporary code (optional)
        - publicKey: ...
        - privateKey ....
        - update_datetime: Timestamp for when the credentials were last updated
        - creation_datetime: Timestamp for when the credentials were created

        non so se public_key sia la chiave pubblica del wallet o la chiave pubblica per l'autenticazione, comunque commento per 
        quello della blockchain è: "The public key associated with the user for accessing their wallet on the blockchain", 
        private blockchain key "The private key associated with the user for accessing their wallet on the blockchain; kept secure and private"

        l'altro è public: "The public key used for the user’s authentication on the platform (separate from the blockchain key)" ?? separato o no poi?
        private : "The private key used for the user’s authentication on the platform (separate from the blockchain key)" 
        """
        super().__init__()
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.public_key = public_key
        self.private_key = private_key
        self.temp_code = temp_code
        self.temp_code_validity = temp_code_validity
        self.publicKey = publicKey
        self.privateKey = privateKey
        self.update_datetime = update_datetime
        self.creation_datetime = creation_datetime

    # Getter methods for each attribute
    def get_id(self):
        return self.id

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_role(self):
        return self.role

    def get_public_key(self):
        return self.public_key

    def get_private_key(self):
        return self.private_key

    def get_temp_code(self):
        return self.temp_code

    def get_temp_code_validity(self):
        return self.temp_code_validity

    def get_publicKey(self):
        return self.publicKey

    def get_privateKey(self):
        return self.privateKey

    def get_update_datetime(self):
        return self.update_datetime

    def get_creation_datetime(self):
        return self.creation_datetime
        
    def save(self):
        """
        Saves a new or updates an existing Credentials record in the database.
        Implements SQL queries to insert or update credentials based on the presence of an ID.
        """
        if self.id is None:
            # Insert new credentials record
            self.cur.execute('''INSERT INTO Credentials (username, password, role, public_key, private_key, temp_code, temp_code_validity, publicKey, privateKey)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', #Question marks as placeholders are used to prevent SQL Injection attacks
                             (self.username, self.password, self.role, self.public_key, self.private_key, 
                              self.temp_code, self.temp_code_validity, self.publicKey, self.privateKey))
            self.id = self.cur.lastrowid # Update the ID with the last row inserted ID if new record
        else:
            # Update existing credentials record
            self.cur.execute('''UPDATE Credentials SET username=?, password=?, role=?, public_key=?, private_key=?, temp_code=?, temp_code_validity=?, publicKey =?, privateKey=? 
                                WHERE id=?''',
                             (self.username, self.password, self.role, self.public_key, self.private_key, 
                              self.temp_code, self.temp_code_validity, self.publicKey, self.privateKey, self.id))
        self.conn.commit()

    def delete(self):
        """
        Deletes a Credentials record from the database based on its ID.
        """
        if self.id is not None:
            self.cur.execute('DELETE FROM Credentials WHERE id=?', (self.id,))
            self.conn.commit()


   