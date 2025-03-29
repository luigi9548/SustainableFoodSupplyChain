import getpass
import re
from eth_utils import *
from eth_keys import *
from controllers.controller import Controller
from controllers.action_controller import ActionController
from session.session import Session
from db.db_operations import DatabaseOperations
from cli.utils import Utils
from colorama import Fore, Style, init


class CommandLineInterface:
    """
    Command-Line Interface (CLI) for a healthcare system.
    Allows users to register, log in, and perform actions based on roles.
    """

    init(convert=True)

    def __init__(self, session: Session):
        """Initialize CLI with a session and controllers."""
        self.controller = Controller(session)
        self.act_controller = ActionController()
        self.session = session
        self.ops = DatabaseOperations()
        self.util = Utils(session)

        self.menu = {
            1: 'Registra utente',
            2: 'Log In',
            3: 'Esci!',
        }


    # lo togliamo ? 
    def print_menu(self):
        """Displays the menu and handles user choices."""
        print(Fore.CYAN + r"""
 ______     _____     __     ______     __  __     ______     __     __   __       
/\  __ \   /\  __-.  /\ \   /\  ___\   /\ \_\ \   /\  __ \   /\ \   /\ "-.\ \      
\ \  __ \  \ \ \/\ \ \ \ \  \ \ \____  \ \  __ \  \ \  __ \  \ \ \  \ \ \-.  \     
 \ \_\ \_\  \ \____-  \ \_\  \ \_____\  \ \_\ \_\  \ \_\ \_\  \ \_\  \ \_\\"\_\    
  \/_/\/_/   \/____/   \/_/   \/_____/   \/_/\/_/   \/_/\/_/   \/_/   \/_/ \/_/   
""" + Style.RESET_ALL)

        for key, value in self.menu.items():
            print(key, '--', value)

        try:
            choice = int(input('Scegli cosa fare: '))

            if choice == 1:
                print('Registra utente')
                self.registration_menu()
            elif choice == 2:
                print('Login')
               # todo action controller e menu 
              
            elif choice == 3:
                print('Esci!')
                exit()
            else:
                print(Fore.RED + 'Wrong choice, insert a valid choise!' + Style.RESET_ALL)

        except ValueError:
            print(Fore.RED + 'Incorrect input, insert a number!\n' + Style.RESET_ALL)

    def registration_menu(self):
        """
        This method prompts users to decide whether to proceed with deployment and 
        initialization of the smart contract. It then collects wallet credentials, 
        personal information, and role selection from the user for registration. 
        The method validates user inputs and interacts with the Controller to perform 
        registration actions.
        """

        contracts = ["SupplyChainRecords.sol", "SupplyChainNFT.sol", "CarbonCreditToken.sol"]


        while True:
            proceed = input("In order to register, you need to deploy. Do you want to proceed with deployment and initialization of the contract? (Y/n): ")
            if proceed.strip().upper() == "Y":
                self.act_controller.deploy_and_initialize(contracts)
                break  # Exit the loop after deployment
            elif proceed.strip().upper() == "N":
                print(Fore.RED + "Deployment cancelled. Please deploy the contracts when you are ready to register." + Style.RESET_ALL)
                return  # Return from the function to cancel
            else:
                print(Fore.RED + 'Wrong input, please insert Y or N!' + Style.RESET_ALL)

        print('Please, enter your wallet credentials.')
        attempts = 0
        while True:
            public_key = input('Public Key: ')
            private_key = getpass.getpass('Private Key: ')
            confirm_private_key = getpass.getpass('Confirm Private Key: ')
            
            if private_key == confirm_private_key:
                if self.controller.check_keys(public_key, private_key):
                    print(Fore.RED + 'A wallet with these keys already exists. Please enter a unique set of keys.' + Style.RESET_ALL)
                    attempts += 1
                    if attempts >= 3:
                        print(Fore.RED + "Maximum retry attempts reached. Redeploying..." + Style.RESET_ALL)
                        self.act_controller.deploy_and_initialize(contracts)
                        attempts = 0  # Reset attempts after deployment
                else:
                    try:
                        pk_bytes = decode_hex(private_key)
                        priv_key = keys.PrivateKey(pk_bytes)
                        pk = priv_key.public_key.to_checksum_address()
                        if pk.lower() != public_key.lower():
                            print(Fore.RED + 'The provided keys do not match. Please check your entries.' + Style.RESET_ALL)
                        else:
                            break
                    except Exception:
                        print(Fore.RED + 'Oops, there is no wallet with the matching public and private key provided.\n' + Style.RESET_ALL)
            else:
                print(Fore.RED + 'Private key and confirmation do not match. Try again.\n' + Style.RESET_ALL)

        
        if is_address(public_key) and (public_key == pk):

            print('Enter your personal information.')

            while True:
                username = input('Username: ')
                if self.controller.check_username(username) == 0: break
                else: print(Fore.RED + 'Your username has been taken.\n' + Style.RESET_ALL)

            while True:
                role = input("Insert your role: \n (C) if certifier \n (F) if farmer \n (R) if carrier \n (S) if seller \n (P) if producer\n Your choice: ").strip().upper()
                if role == 'C':
                    user_role = 'CERTIFIER'
                    confirm = input("Do you confirm you're a certifier? (Y/n): ").strip().upper()
                    if confirm == 'Y':
                        break
                    else:
                        print(Fore.RED + "Role not confirmed. Retry\n" + Style.RESET_ALL)
                elif role == 'F':
                    user_role = 'FARMER'
                    confirm = input("Do you confirm you're a farmer? (Y/n): ").strip().upper()
                    if confirm == 'Y':
                        break
                    else:
                        print(Fore.RED + "Role not confirmed. Retry\n" + Style.RESET_ALL)
                elif role == 'R':
                    user_role = 'CARRIER'
                    confirm = input("Do you confirm you're a carrier? (Y/n): ").strip().upper()
                    if confirm == 'Y':
                        break
                    else:
                        print(Fore.RED + "Role not confirmed. Retry\n" + Style.RESET_ALL)
                elif role == 'S':
                    user_role = 'SELLER'
                    confirm = input("Do you confirm you're a seller? (Y/n): ").strip().upper()
                    if confirm == 'Y':
                        break
                    else:
                        print(Fore.RED + "Role not confirmed. Retry\n" + Style.RESET_ALL)
                elif role == 'P':
                    user_role = 'PRODUCER'
                    confirm = input("Do you confirm you're a producer? (Y/n): ").strip().upper()
                    if confirm == 'Y':
                        break
                    else:
                        print(Fore.RED + "Role not confirmed. Retry\n" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "You have to select a role between (C) certifier, (F) farmer, (R) carrier, (S) seller, (P) producer. Retry\n" + Style.RESET_ALL)
        
            while True:
                while True:
                    password = getpass.getpass('Password: ')
                    passwd_regex = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=])(?!.*\s).{8,100}$'
                    if not re.fullmatch(passwd_regex, password):
                        print(Fore.RED + 'Password must contain at least 8 characters, at least one digit, at least one uppercase letter, one lowercase letter, and at least one special character.\n' + Style.RESET_ALL)
                    else: break

                confirm_password = getpass.getpass('Confirm Password: ')
                
                if password != confirm_password:
                    print(Fore.RED + 'Password and confirmation do not match. Try again\n' + Style.RESET_ALL)
                else:
                    break

            reg_code = self.controller.registration(username, password, user_role, public_key, private_key)
            if reg_code == 0:
                print(Fore.GREEN + 'You have succesfully registered!\n' + Style.RESET_ALL)
                if role == 'C':
                    self.insert_actor_info(username, 'CERTIFIER')
                elif role == 'F':
                    self.insert_actor_info(username, 'FARMER')
                elif role == 'R':
                    self.insert_actor_info(username, 'CARRIER')
                elif role == 'S':
                    self.insert_actor_info(username, 'SELLER')
                elif role == 'P':
                    self.insert_actor_info(username, 'PRODUCER')
            elif reg_code == -1:
                print(Fore.RED + 'Your username has been taken.\n' + Style.RESET_ALL)
        
        else:
            print(Fore.RED + 'Sorry, but the provided public and private key do not match to any account\n' + Style.RESET_ALL)
            return 

    def insert_actor_info(self, username, role):
        """
        This method assists actors in providing their personal information. It validates 
        user inputs and ensures data integrity before inserting the information into 
        the system. Additionally, it registers the actor entity on the blockchain.

        Args:
            username (str): The username of the actor.
            role (str): The role of the actor.
        """

        print("\nProceed with the insertion of a few personal information.")
        while True:
            name = input('Name: ')
            if self.controller.check_null_info(name): break
            else: print(Fore.RED + '\nPlease insert information.' + Style.RESET_ALL)
        while True:
            lastname = input('Lastname: ')
            if self.controller.check_null_info(lastname): break
            else: print(Fore.RED + '\nPlease insert information.' + Style.RESET_ALL)
        while True:
            actorLicense = input('License: ') #TODO aggiungere opportuni controlli sulla licenza
            if self.controller.check_null_info(actorLicense): break
            else: print(Fore.RED + '\nPlease insert information.' + Style.RESET_ALL)
        while True:
            residence = input('Residence: ')
            if self.controller.check_null_info(residence): break
            else: print(Fore.RED + '\nPlease insert information.' + Style.RESET_ALL)
        while True:
            birthdayPlace = input('Birthday place: ')
            if self.controller.check_null_info(birthdayPlace): break
            else: print(Fore.RED + '\nPlease insert information.' + Style.RESET_ALL)
        while True:
            birthday = input('Date of birth (YYYY-MM-DD): ')
            if self.controller.check_birthdate_format(birthday): break
            else: print(Fore.RED + "Invalid birthdate or incorrect format." + Style.RESET_ALL)
        while True:
            mail = input('E-mail: ')
            if self.controller.check_email_format(mail): 
                if self.controller.check_unique_email(mail) == 0: break
                else: print(Fore.RED + "This e-mail has already been inserted. \n" + Style.RESET_ALL)
            else: print(Fore.RED + "Invalid e-mail format.\n" + Style.RESET_ALL)
        while True:
            phone = input('Phone number: ')
            if self.controller.check_phone_number_format(phone): 
                if self.controller.check_unique_phone_number(phone) == 0: break
                else: print(Fore.RED + "This phone number has already been inserted. \n" + Style.RESET_ALL)
            else: print(Fore.RED + "Invalid phone number format.\n" + Style.RESET_ALL)

        from_address_actor = self.controller.get_public_key_by_username(username)
        self.act_controller.register_entity(role, name, lastname, from_address=from_address_actor)
        insert_code = self.controller.insert_actor_info(role, username, name, lastname, actorLicense, residence, birthdayPlace, birthday, mail, phone)
        if insert_code == 0:
            print(Fore.GREEN + 'Information saved correctly!' + Style.RESET_ALL)
            if role == 'CERTIFIER':
                self.certifier_menu(username)
            """
            elif role == 'F':
                self.medic_menu(username)
            elif role == 'R':
                self.medic_menu(username)
            elif role == 'S':
                self.medic_menu(username)
            elif role == 'P':
                self.medic_menu(username)"""
            # self.medic_menu(username) Inserire switch case per i vari ruoli 
        elif insert_code == -1:
            print(Fore.RED + 'Internal error!' + Style.RESET_ALL)
    
    def certifier_menu(self, username):
        """
        This method presents certifier with a menu of options tailored to their role. 
        It allows certifier to choose actions such as selecting a patient, viewing or 
        updating their profile, changing their password, or logging out. The method 
        handles user input validation and directs users to the corresponding functionality 
        based on their choice.

        Args:
            username (str): The username of the logged-in certifier.
        """

        certifier_options = {
            1: "View activities to be processed",
            2: "View user activities",
            3: "View users data",
            4: "View user data",
            5: "View products data", 
            6: "Assign Carbon credits",
            7: "Remove Carbon credits",
            8: "View profile",
            9: "Update profile",
            10: "Change password",
            11: "Log out"
        }

        while True:
            print(Fore.CYAN + "\nMENU" + Style.RESET_ALL)                           
            for key, value in certifier_options.items():
                print(f"{key} -- {value}")
                                                
            try:                                    
                choice = int(input("Choose an option: "))
                if choice in certifier_options:
                    if choice == 1:
                        self.util.view_activitiesToBeProcessed()

                    elif choice == 2:
                        username = input("Enter the username of the user whose activities you want to view: ")
                        self.util.view_userActivities(username)

                    elif choice == 3:
                        self.util.view_usersView()

                    elif choice == 4:
                        username = input("Enter the username of the user whose profile you want to view: ")
                        self.util.view_userView(username, "\nUSER INFO\n")

                    elif choice == 8:
                        self.util.view_userView(username, "\nCERTIFIER INFO\n")

                    elif choice == 9:                           
                        self.util.update_profile(username, "CERTIFIER")
                
                    elif choice == 10:
                        self.util.change_passwd(username)

                    elif choice == 11:
                        confirm = input("\nDo you really want to leave? (Y/n): ").strip().upper()
                        if confirm == 'Y':
                            print(Fore.CYAN + "\nThank you for using the service!\n" + Style.RESET_ALL)
                            self.session.reset_session()
                            return
                        else:
                            print(Fore.RED + "Invalid choice! Please try again." + Style.RESET_ALL)

            except ValueError:
                print(Fore.RED + "Invalid Input! Please enter a valid number." + Style.RESET_ALL)

if __name__ == "__main__":
    session = Session()
    cli = CommandLineInterface(session)
    cli.print_menu()