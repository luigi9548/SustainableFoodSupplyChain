"""
This module provides various utility functions for handling user input, updating profiles, changing passwords, 
displaying data etc..
"""

import datetime
import math
import re
import click
import getpass
from colorama import Fore, Style, init
from rich.console import Console
from rich.table import Table

from controllers.controller import Controller
from controllers.action_controller import ActionController
from session.session import Session
from session.logging import log_error



class Utils:
    """
    Attributes:
        PAGE_SIZE (int): The number of items to display per page.
        current_page (int): The index of the current page being displayed.

    """

    init(convert=True)

    PAGE_SIZE = 3
    current_page = 0
    
    def __init__(self, session: Session):

        """
        Initializes the Utils class with a session object.

        Parameters:
            session (Session): The session object containing user information.

        Attributes:
            session (Session): The session object containing user information.
            controller (Controller): An instance of the Controller class for database interaction.
            act_controller (ActionController): An instance of the ActionController class for managing actions.
            today_date (str): The current date in string format.
        """

        self.session = session
        self.controller = Controller(session)
        self.act_controller = ActionController()
        self.today_date = str(datetime.date.today())

    def update_profile(self, username, role):
        """
        Updates the profile information of a user.

        Parameters:
            username (str): The username of the user whose profile is being updated.
            role (str): The role of the user.

        Returns:
            None
        """
     
        print(Fore.CYAN + "\nUpdate profile function"  + Style.RESET_ALL)
        us = self.controller.get_user_by_username(username)

        print("\nEnter your new Information...")
        us.set_name(click.prompt('Name ', default=us.get_name()))
        us.set_lastname(click.prompt('Lastname ', default=us.get_lastname()))
        while True:
            birthday = click.prompt('Date of birth (YYYY-MM-DD) ', default=us.get_birthday())
            if self.controller.check_birthdate_format(birthday): 
                us.set_birthday(birthday)
                break
            else: print(Fore.RED + "Invalid birthdate or incorrect format." + Style.RESET_ALL)
        us.set_birth_place(click.prompt('Birth place ', default=us.get_birth_place()))
        us.set_residence(click.prompt('Residence ', default=us.get_residence()))
        while True:
            mail = click.prompt('E-mail ', default=us.get_mail())
            if self.controller.check_email_format(mail): 
                us.set_mail(mail)
                break
            else: print(Fore.RED + "Invalid e-mail format.\n" + Style.RESET_ALL)
        while True:
            phone = click.prompt('Phone ', default=us.get_phone())
            if self.controller.check_phone_number_format(phone): 
                us.set_phone(phone)
                break
            else: print(Fore.RED + "Invalid phone number format."  + Style.RESET_ALL)
            
        name = us.get_name()
        lastname = us.get_lastname()
        try:
            from_address_actor = self.controller.get_public_key_by_username(username)
            self.act_controller.update_entity(role, name, lastname, from_address=from_address_actor)
        except Exception as e:
            log_error(e)

        result = self.controller.update_actor_info(us)

        if result == 0:
            print(Fore.GREEN + 'Information saved correctly!\n' + Style.RESET_ALL)
        else:
            print(Fore.RED + 'Error saving information!\n' + Style.RESET_ALL)

    def view_userView(self, username, userInfo):
        """
        This method retrieves and displays the profile information of the user 
        identified by the given username.

        Args:
            username (str): The username of the user whose profile is to be viewed.
            userInfo (str): The type of user whose profile is to be viewed.

        """

        userView = self.controller.get_user_by_username(username)
        print(Fore.CYAN + userInfo + Style.RESET_ALL)
        print("Username: ", userView.get_username())
        print("Name: ", userView.get_name())
        print("Lastname: ", userView.get_lastname())
        print("License: ", userView.get_licence_id())
        print("Birthday: ", userView.get_birthday())
        print("Birthday place: ", userView.get_birth_place())
        print("Residence: ", userView.get_residence())
        print("E-mail: ", userView.get_mail())
        print("Phone: ",userView.get_phone())
        input("\nPress Enter to exit\n")

    def view_usersView(self):
        """
        This method retrieves and displays the profile information of all users.
        """
        users = self.controller.get_users()
        print(Fore.CYAN + "USERS:" + Style.RESET_ALL)
        print("\n")
        if users:
            for user in users:
                print("Username: ", user.get_username())
                print("Name: ", user.get_name())
                print("Lastname: ", user.get_lastname())
                print("License: ", user.get_licence_id())
                print("Birthday: ", user.get_birthday())
                print("Birthday place: ", user.get_birth_place())
                print("Residence: ", user.get_residence())
                print("E-mail: ", user.get_mail())
                print("Phone: ",user.get_phone())
                print("\n")
        else:
            print("No users found.\n")
    
    def view_activitiesToBeProcessed(self):
        """
        This method retrieves and displays the activities that are pending processing.
        """
        activities = self.controller.get_activities_to_be_processed()
        print(Fore.CYAN + "Activities to be processed:" + Style.RESET_ALL)
        print("\n")
        if activities:
            for act in activities:
                print("Activity ID: ", act.get_id())
                print("Actor username: ", act.get_username())
                print("Activity description: ", act.get_description())
                print("Activity update date: ", act.get_update_datetime())
                print("Activity creation date: ", act.get_creation_datetime())
                print("Activity CO2 reduction: ", act.get_co2_reduction())
                print("Activity state: ", act.get_state())
                print("\n")
        else:
            print("No activities to be processed.\n")

    def view_userActivities(self, username):
        """
        This method retrieves and displays the activities of the current user.

        Args:
            username (str): The username of the user whose activities are to be viewed.
        """
        activities = self.controller.get_activities_by_username(username)
        print(Fore.CYAN + username + " activities:" + Style.RESET_ALL)
        print("\n")
        if activities:
            for act in activities:
                print("Activity ID: ", act.get_id())
                print("Activity description: ", act.get_description())
                print("Activity update date: ", act.get_update_datetime())
                print("Activity creation date: ", act.get_creation_datetime())
                print("Activity CO2 reduction: ", act.get_co2_reduction())
                print("Activity state: ", act.get_state())
                print("\n")
        else:
            print("No activities found.\n")
