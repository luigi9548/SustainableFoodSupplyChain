"""
This module provides various utility functions for handling user input, updating profiles, changing passwords, 
displaying data etc..
"""

import datetime
import re
import click
import random
from colorama import Fore, Style, init
import maskpass
import os

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

    def __init__(self, session: Session, act_controller : ActionController):

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
        self.act_controller = act_controller
        self.today_date = str(datetime.date.today())

    def contract_files_exist(self, contract_names_or_files, contracts_dir="on_chain"):
        """
        Checks if both the ABI and address files exist for each given contract.

        Args:
            contract_names_or_files (list): List of contract names or filenames (e.g., "CarbonCreditToken.sol").
            contracts_dir (str): Directory where ABI and address files are stored.

        Returns:
            bool: True if all required files exist, False otherwise.
        """
        for item in contract_names_or_files:
            contract_name = os.path.splitext(os.path.basename(item))[0]  # Remove path and extension

            abi_path = os.path.join(contracts_dir, f"{contract_name}_abi.json")
            address_path = os.path.join(contracts_dir, f"{contract_name}_address.txt")

            if not (os.path.exists(abi_path) and os.path.exists(address_path)):
                return False

        return True


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

    def change_passwd(self, username):
        """
        Allows the user to change their password.

        Args:
            username (str): The username of the user whose password is being changed.

        Returns:
            None
        """
        while True:
            confirmation = input("Do you want to change your password (Y/n): ").strip().upper()
            if confirmation == 'Y':
                while True:
                    old_pass = maskpass.askpass('Old Password: ', mask="*")
                    if not self.controller.check_credentials(username, old_pass):
                        print(Fore.RED + '\nYou entered the wrong old password.\n' + Style.RESET_ALL)
                        continue
                    else:
                        while True:
                            new_passwd = maskpass.askpass('New password: ', mask="*")
                            new_confirm_password = maskpass.askpass('Confirm new password: ', mask="*")

                            passwd_regex = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=!?])(?!.*\s).{8,100}$'
                            if not re.fullmatch(passwd_regex, new_passwd):
                                print(Fore.RED + 'Password must contain at least 8 characters, at least one digit, at least one uppercase letter, one lowercase letter, and at least one special character.\n' + Style.RESET_ALL)
                            elif new_passwd != new_confirm_password:
                                print(Fore.RED + 'Password and confirmation do not match. Try again\n' + Style.RESET_ALL)
                            else:
                                response = self.controller.update_password(username, new_passwd)
                                if response == 0:
                                    print(Fore.GREEN + '\nPassword changed correctly!\n' + Style.RESET_ALL)
                                elif response == -1 or response == -2:
                                    print(Fore.RED + '\nSorry, something went wrong!\n' + Style.RESET_ALL)
                                break
                        break
            else:
                print("Okay\n")
            break

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

    def is_valid_activity_id(self, activity_id, activities):
        return any(act.get_id() == activity_id for act in activities)

    def view_userActivities(self, username, activities):
        """
        This method retrieves and displays the activities of the current user.

        Args:
            username (str): The username of the user whose activities are to be viewed.
            activities (list): A list of activities associated with the user.
        """
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

    def create_nft(self, username):
        """
        Collects NFT data from the user and mints a new NFT.
        """

        print(Fore.CYAN + "\nNFT Creation - Enter the required details:" + Style.RESET_ALL)
        while True:
            name = input("Product Name: ").strip()
            if self.controller.check_null_info(name): break
            else: print(Fore.RED + '\nPlease insert information.' + Style.RESET_ALL)
        """while True:
            category = input("Product Category (Fruit, Meat, Dairy): ").strip()
            if self.controller.check_null_info(category): break
            else: print(Fore.RED + '\nPlease insert information.' + Style.RESET_ALL)"""
        while True:
            category = click.prompt("Product category (FRUIT / MEAT / DAIRY)").upper()
            if category in ["FRUIT", "MEAT", "DAIRY"]:
                break
            else:
                print(Fore.RED + "Invalid category. Choose one of: FRUIT, MEAT, DAIRY" + Style.RESET_ALL)

        emissions = random.randint(1,100)
        quality_score = random.randint(1,100)
        role = "FARMER"
        harvest_date = self.today_date

        from_address = self.controller.get_public_key_by_username(username)
        to_address = self.controller.get_public_key_by_username(username)

        # Chiamata alla funzione che interagisce con lo smart contract
        self.act_controller.create_nft(
            to_address,
            role,
            name,
            category,
            emissions,
            quality_score,
            int(datetime.datetime.strptime(harvest_date, "%Y-%m-%d").timestamp()),
            from_address=from_address
        )

        nft_token_id = self.act_controller.get_last_id()

        result = self.controller.create_product(name, category, emissions, nft_token_id)

        if result == 0:
            print(Fore.GREEN + 'Product created correctly!\n' + Style.RESET_ALL)
        else:
            print(Fore.RED + 'Error creating information!\n' + Style.RESET_ALL)

    def update_nft(self, username):
        """
        Updates an existing NFT's CO₂ emissions.

        Args:
            username (str): The username of the user performing the update.

        Returns:
            dict: Transaction receipt if successful, else an error message.
        """
        while True:
            nft_id = input("ID ntf to modify: ").strip()
            if nft_id.isdigit() and int(nft_id) >= 0:
                nft_id = int(nft_id)
                break
            else:
                print(Fore.RED + 'Invalid input. Enter a positive numeric value.' + Style.RESET_ALL)
        from_address = self.controller.get_public_key_by_username(username)
        emissions = random.randint(1,100)

        # Chiamata alla funzione che interagisce con lo smart contract
        self.act_controller.update_nft(nft_id, emissions, from_address=from_address)

        emissionsTot = self.act_controller.get_emissions_by_nft_id(nft_id)
        result = self.controller.update_product(nft_id, emissionsTot)

    def transfer_nft(self, username, role):
        """
        Transfers an NFT from one user to another.
        Args:
            username (str): The username of the user performing the transfer.
            role (str): The role of the user performing the transfer.
        Returns:
            dict: Transaction receipt if successful, else an error message.
        """
        while True:
            nft_id = input("ID ntf to transfer: ").strip()
            if nft_id.isdigit() and int(nft_id) >= 0:
                nft_id = int(nft_id)
                break
            else:
                print(Fore.RED +
                      'Invalid input. Enter a positive numeric value.' +
                      Style.RESET_ALL)

        while True:
            to_username = input("Username of the new owner: ").strip()
            if not self.controller.check_null_info(to_username):
                print(Fore.RED + '\nPlease insert information.' + Style.RESET_ALL)
                continue

            to_user = self.controller.get_user_by_username(to_username)
            if to_user:
                break
            else:
                print(Fore.RED + '\nNo user found with this username.' + Style.RESET_ALL)

        to_address = self.controller.get_public_key_by_username(to_username)
        to_role = to_user.type
        from_address = self.controller.get_public_key_by_username(username)

        # Check if the transfer is valid
        if not self.is_valid_transfer(role, to_role):
            print(Fore.RED + 'Transfer not allowed between these roles.\n' + Style.RESET_ALL)
            return

        proceed = input(f"Do you want to transfer the NFT from {role} to {to_role}? (Y/n): ")
        if proceed.strip().upper() == "Y":
            # Chiamata alla funzione che interagisce con lo smart contract
            receipt = self.act_controller.transfer_nft(nft_id, to_address, to_role, from_address)
            if receipt.get('status') == 1:
                print(Fore.GREEN + 'Product transferred correctly!\n' +
                      Style.RESET_ALL)
            else:
                print(Fore.RED + 'Error transferring product!\n' + Style.RESET_ALL)
        else:
            print("NFT transfer canceled.")

    def is_valid_transfer(self, from_role: str, to_role: str) -> bool:
        """
        Checks if a transfer between two roles is valid based on predefined rules.
        Args:
            from_role (str): The role of the sender.
            to_role (str): The role of the recipient.
            Returns:
                bool: True if the transfer is valid, False otherwise.
        """

        valid_transitions = {
            "FARMER": "CARRIER",
            "CARRIER": ["PRODUCER", "SELLER"],
            "PRODUCER": "CARRIER"
        }

        # Normalizza i ruoli a lettere maiuscole (come nella logica Solidity)
        from_role = from_role.upper()
        to_role = to_role.upper()

        allowed = valid_transitions.get(from_role)

        if isinstance(allowed, list):
            return to_role in allowed
        return to_role == allowed

    def display_user_nfts(self, username):
        """
        Retrieves and displays all NFTs owned by a specific user.
    
        Args:
            username (str): The username of the owner whose NFTs will be displayed.
        """
        # Get the user's Ethereum address from their username
        user_address = self.controller.get_public_key_by_username(username)

        if not user_address:
            print(Fore.RED + f"Could not find address for user: {username}" + Style.RESET_ALL)
            return

        # Call the action controller to get the NFT data
        nft_data = self.act_controller.get_nft_data_by_owner(user_address)
        ids, names, categories, emissions, scores, harvests = nft_data

        # Display the NFTs in a formatted table
        if len(ids) == 0:
            print(Fore.YELLOW + f"User {username} does not own any NFTs." + Style.RESET_ALL)
            return

        print(Fore.GREEN + f"\nNFTs owned by {username} (address: {user_address}):" + Style.RESET_ALL)
        print("-" * 82)
        print(f"{'ID':<5} {'Name':<15} {'Category':<15} {'CO2 Emission':<15} {'Quality Score':<15} {'Harvest Date':<15}")
        print("-" * 82)

        for i in range(len(ids)):
            # Convert harvest date from Unix timestamp to readable format if needed
            harvest_date = datetime.datetime.fromtimestamp(harvests[i]).strftime('%Y-%m-%d') if harvests[i] > 0 else "N/A"

            print(f"{ids[i]:<5} {names[i]:<15} {categories[i]:<15} {emissions[i]:<15} {scores[i]:<15} {harvest_date:<15}")

        print("-" * 82)

    def assign_carbon_credits(self, username, co2Amount, activity_id, from_address_actor):
        """
        This method assigns carbon credits to users based on their activities.

        Args:
            username (str): The username of the user to whom carbon credits are to be assigned.
            co2Amount (int): The amount of carbon credits to be assigned.
            activity_id (int): The ID of the activity for which carbon credits are to be assigned.
            from_address_actor (str): The public key of the actor assigning the carbon credits.
        """
        address_to = self.controller.get_public_key_by_username(username)
        transaction_receipt = self.act_controller.assign_carbon_credits(address_to, co2Amount, from_address=from_address_actor)
        self.controller.update_activity_state(activity_id)
        return transaction_receipt

    def view_user_balance(self, username):
        """
        This method retrieves and displays the balance of the user identified by the given username.

        Args:
            username (str): The username of the user whose balance is to be viewed.
        """
        user_key = self.controller.get_public_key_by_username(username)
        balance = self.act_controller.get_balance(user_key)
        print(f"{username} balance: {balance}")
        input("\nPress Enter to exit\n")

    def find_helper_in_supply_chain(self, balance, creditor_pk):
        """
        This method finds and returns the helper in the supply chain 
        with the highest carbon credit balance that can cover the deficit.

        Args:
            balance (int): The amount of carbon credits in deficit.
            creditor_pk (str): The public key of the creditor.

        Returns:
            str or None: The public key of the helper, or None if none can help.
        """
        helpers_public_keys = self.controller.get_helpers()

        if creditor_pk in helpers_public_keys:
            helpers_public_keys.remove(creditor_pk)

        helper_candidates = []

        for public_key in helpers_public_keys:
            amount = self.act_controller.get_balance(public_key)
            if amount >= balance:
                helper_candidates.append((public_key, amount))

        if not helper_candidates:
            return None

        best_helper = max(helper_candidates, key=lambda x: x[1])
        return best_helper[0]

    def view_user_transactions(self, username, tranasactions):
        """
        This method retrieves and displays the transactions of the current user.

        Args:
            username (str): The username of the user whose transactions are to be viewed.
            tranasactions (list): A list of tranasactions associated with the user.
        """
        print(Fore.CYAN + username + " tranasactions:" + Style.RESET_ALL)
        print("\n")
        if tranasactions:
            for tran in tranasactions:
                print("Transaction ID: ", tran.get_id())
                print("Transaction sender: ", tran.get_username_from())
                print("Transaction recipient: ", tran.get_username_to())
                print("Transaction amount: ", tran.get_amount())
                print("Transaction type: ", tran.get_type())
                print("Transaction hash: ", tran.get_tx_hash())
                print("Transaction creation date: ", tran.get_timestamp())
                print("\n")
        else:
            print("No transactions found.\n")

    def add_user_activity(self, username: str, role: str):
        """
        Allows a logged-in user to add a new activity to the system and link it to the user's account.

        Args:
            username (str): The username of the logged-in user.
            role (str): The user's role (FARMER, CARRIER, SELLER, PRODUCER, CERTIFIER).

        Returns:
            None
        """
        print(Fore.GREEN + "\n--- Add a New Activity ---" + Style.RESET_ALL)
        try:
            print("Available types:")
            print("1 -- Investment in a project for reduction")
            print("2 -- Performing an action")

            while True:
                type_choice = input("Select the type of activity (1 or 2): ").strip()
                if type_choice == "1":
                    activity_type = "investment in a project for reduction"
                    break
                elif type_choice == "2":
                    activity_type = "performing an action"
                    break
                else:
                    print(Fore.RED + "Invalid choice. Please select 1 or 2." + Style.RESET_ALL)

            description = input("Enter a brief description of the activity: ").strip()

            activity_id = self.controller.register_activities(activity_type, description)
            self.controller.register_account_activities(username, activity_id)

            co2_reduction = round(random.uniform(10.0, 100.0), 2)  # simulate environmental impact
            self.controller.register_cron_activity(description, username, 0, activity_id, co2_reduction)

            print(Fore.CYAN + "Activity successfully added and logged!" + Style.RESET_ALL)

        except Exception as e:
            print(Fore.RED + f"Error while adding the activity: {str(e)}" + Style.RESET_ALL)
