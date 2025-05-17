"""
This module contains the Session class which manages user sessions, including login attempts,
timeouts, and user session data.
"""
import time

class Session:
    """
    A Session class to handle the state of a user session, including the current user,
    login attempts, and timeout handling.
    """

    def __init__(self):
        """
        Initializes a new session.

        Initial attributes:
        - __user: No user is logged in (None).
        - __attempts: Number of failed login attempts, initially 0.
        - __login_error_timestamp: Timestamp for login timeout, initially 0.
        """
        self.__user = None
        self.__attempts = 0
        self.__login_error_timestamp = 0
    
    def set_user(self, user):
        """
        Sets the current user for the session.

        Args:
            user (any): The user object to associate with this session.
        """
        self.__user = user

    def get_attempts(self):
        """
        Returns the number of failed login attempts.

        Returns:
            int: The current count of failed login attempts.
        """
        return self.__attempts
    
    def increment_attempts(self):
        """
        Increments the number of login attempts by one.
        """
        self.__attempts += 1

    def reset_attempts(self):
        """
        Resets the number of login attempts to zero.
        """
        self.__attempts = 0

    def set_error_attempts_timeout(self, timeout: int):
        """
        Sets a timeout after a failed login attempt, blocking further attempts for a period.

        Args:
            timeout (int): Duration of the timeout in seconds.
        """
        self.__login_error_timestamp = time.time() + timeout

    def get_timeout_left(self):
        """
        Returns the remaining time before the login block is lifted.

        Returns:
            float: Time left in seconds before login is allowed again.
                   Returns 0 if the timeout has expired.
        """
        return max(0, self.__login_error_timestamp - time.time())

    def reset_session(self):
        """
        Resets the session to its initial state with no user, 
        no login attempts, and no timeout.
        """
        self.__user = None
        self.__attempts = 0
        self.__login_error_timestamp = 0
