import getpass
import re
from eth_utils import decode_hex
from eth_keys import keys
#from controllers.controller import Controller
from controllers.action_controller import ActionController
from session.session import Session
from db.db_operations import DatabaseOperations
#from cli.utils import Utils
from colorama import Fore, Style, init


class CommandLineInterface:
    """
    Command-Line Interface (CLI) for a healthcare system.
    Allows users to register, log in, and perform actions based on roles.
    """

    init(convert=True)

    def __init__(self, session: Session):
        """Initialize CLI with a session and controllers."""
        #self.controller = Controller(session)
        self.act_controller = ActionController()
        self.session = session
        self.ops = DatabaseOperations()
        #self.util = Utils(session)

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
                print(Fore.RED + 'Scelta sbagliata inserisci una scelta valida!' + Style.RESET_ALL)

        except ValueError:
            print(Fore.RED + 'Input non corretto, inserisci un numero!\n' + Style.RESET_ALL)

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
                role = input("Insert your role: \n (C) if caregiver \n (M) if medic\n (P) if patient \n Your choice: ").strip().upper()
                if role == 'M':
                    user_role = 'MEDIC'
                    confirm = input("Do you confirm you're a Medic? (Y/n): ").strip().upper()
                    if confirm == 'Y':
                        break
                    else:
                        print(Fore.RED + "Role not confirmed. Retry\n" + Style.RESET_ALL)
                elif role == 'P':
                    user_role = 'PATIENT'
                    confirm = input("Do you confirm you're a Patient? (Y/n): ").strip().upper()
                    if confirm == 'Y':
                        break
                    else:
                        print(Fore.RED + "Role not confirmed. Retry\n" + Style.RESET_ALL)
                elif role == 'C':
                    user_role = 'CAREGIVER'
                    confirm = input("Do you confirm you're a Caregiver? (Y/n): ").strip().upper()
                    if confirm == 'Y':
                        break
                    else:
                        print(Fore.RED + "Role not confirmed. Retry\n" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "You have to select a role between Caregiver (C), Medic (M) or Patient (P). Retry\n" + Style.RESET_ALL)
        
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
                if role == 'P':
                    self.insert_patient_info(username)
                elif role == 'M':
                    self.insert_medic_info(username)
                elif role == 'C':
                    self.insert_caregiver_info(username)
            elif reg_code == -1:
                print(Fore.RED + 'Your username has been taken.\n' + Style.RESET_ALL)
        
        else:
            print(Fore.RED + 'Sorry, but the provided public and private key do not match to any account\n' + Style.RESET_ALL)
            return 
    


if __name__ == "__main__":
    session = Session()
    cli = CommandLineInterface(session)
    cli.print_menu()