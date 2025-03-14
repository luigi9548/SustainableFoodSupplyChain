import getpass
import re
from eth_utils import decode_hex
from eth_keys import keys
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
                # todo action controller e menu 
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

    


if __name__ == "__main__":
    session = Session()
    cli = CommandLineInterface(session)
    cli.print_menu()