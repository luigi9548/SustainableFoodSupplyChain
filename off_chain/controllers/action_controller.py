from calendar import c
import os
import time
import json
from colorama import Fore, Style, init
from controllers.deploy_controller import DeployController
from session.logging import log_msg, log_error
from web3 import Web3

class ActionController:
    """
    ActionController interacts with the Ethereum blockchain through methods defined in the contract.
    Connection with provider is established thanks to DeployController and Web3.
    """

    init(convert=True)

    def __init__(self, http_provider='http://ganache:8545'):
        """
        Initialize the ActionController to interact with an Ethereum blockchain.

        Args:
            http_provider (str): The HTTP URL to connect to an Ethereum node.
        """
        #http://ganache:8545
        #http://127.0.0.1:8545
        self.http_provider = http_provider
        self.w3 = Web3(Web3.HTTPProvider(self.http_provider))
        assert self.w3.is_connected(), Fore.RED + "Failed to connect to Ethereum node." + Style.RESET_ALL
        self.load_contracts()

    def load_contracts(self, contracts_directory="on_chain/"):
        """
        Load multiple contracts using their ABI and address from separate files.
        Logs error if files are missing or contents are invalid.

        Args:
            contracts_directory (str): Directory where contract files are stored.
        """
        self.contracts = {}  # Dictionary to store uploaded contracts
        address_path = ""
        abi_path = ""
        contract_name = ""

        try:
            for filename in os.listdir(contracts_directory):
                if filename.endswith("_address.txt"):
                    contract_name = filename.replace("_address.txt", "")
                    address_path = os.path.join(contracts_directory, filename)
                    abi_path = os.path.join(contracts_directory, f"{contract_name}_abi.json")

                # Verifica che entrambi i file esistano
                if os.path.exists(address_path) and os.path.exists(abi_path):
                    with open(address_path, 'r') as file:
                        contract_address = file.read().strip()
                    with open(abi_path, 'r') as file:
                        contract_abi = json.load(file)

                    if contract_address and contract_abi:
                        self.contracts[contract_name] = self.w3.eth.contract(
                            address=contract_address, abi=contract_abi
                        )
                        log_msg(f"Contract '{contract_name}' loaded with address: {contract_address}")
                    else:
                        log_error(f"Invalid data in files for contract '{contract_name}'. Please check the files.")
                else:
                    log_error(f"Missing files for contract '{contract_name}'. Expected {contract_name}_address.txt and {contract_name}_abi.json.")

            if not self.contracts:
                log_error("No valid contracts found. Deploy contracts first.")
                print(Fore.RED + "No valid contracts found. Deploy contracts first." + Style.RESET_ALL)

        except FileNotFoundError:
            log_error("Contracts directory not found.")
            print(Fore.RED + "Contracts directory not found." + Style.RESET_ALL)

    def deploy_and_initialize(self, contract_source_paths=None):
        """
        Deploys and initializes multiple smart contracts.

        Args:
            contract_source_paths (list): List of Solidity contract source file paths.
                                          Default is None, meaning no contract is deployed.
        """
        if contract_source_paths is None:
            log_error("No contract source paths provided.")
            print(Fore.RED + "No contract source paths provided." + Style.RESET_ALL)
            return

        try:
            controller = DeployController(self.http_provider)

            # Assicurati che la cartella on_chain esista
            contracts_dir = os.path.join(os.path.dirname(__file__), "../../on_chain")

            for contract_source_path in contract_source_paths:
                contract_name = os.path.splitext(os.path.basename(contract_source_path))[0]  # Es: "SupplyChainRecords"

                # Percorso completo del file Solidity
                full_path = os.path.join(contracts_dir, contract_source_path)

                # Compilazione e deploy
                controller.compile_and_deploy(full_path)
                contract = controller.contract

                # Scrittura dei file separati
                address_path = os.path.join(contracts_dir, f"{contract_name}_address.txt")
                abi_path = os.path.join(contracts_dir, f"{contract_name}_abi.json")

                with open(address_path, 'w') as file:
                    file.write(contract.address)

                with open(abi_path, 'w') as file:
                    json.dump(contract.abi, file)

                self.load_contracts()

                log_msg(f"Contract '{contract_name}' deployed at {contract.address} and initialized.")

        except Exception as e:
            log_error(str(e))
            print(Fore.RED + "An error occurred during deployment." + Style.RESET_ALL)

    def read_data(self, function_name, contract_name, *args):
        """
        Reads data from a contract's function.

        Args:
            function_name (str): The name of the function to call.
            contract_name (str): The name of the contract to use.
            *args: Arguments required by the contract function.

        Returns:
            The result returned by the contract function.
        """
        try:
            result = self.contracts[contract_name].functions[function_name](*args).call()
            log_msg(f"Data read from function: {function_name}, contract: {contract_name}: {result}")
            return result
        except Exception as e:
            log_error(f"Failed to read data from function: {function_name}, contract: {contract_name}: {str(e)}")
            raise e

    def write_data(self, function_name, contract_name, from_address, *args, gas=2000000, gas_price=None, nonce=None):
        """
        Writes data to a contract's function.

        Args:
            function_name (str): The function name to call on the contract.
            contract_name (str): The name of the contract to use.
            from_address (str): The Ethereum address to send the transaction from.
            *args: Arguments required by the function.
            gas (int): The gas limit for the transaction.
            gas_price (int): The gas price for the transaction.
            nonce (int): The nonce for the transaction.

        Returns:
            The transaction receipt object.
        """
        if not from_address:
            raise ValueError("Invalid 'from_address' provided. It must be a non-empty string representing an Ethereum address.")
        tx_parameters = {
            'from': from_address,
            'gas': gas,
            'gasPrice': gas_price or self.w3.eth.gas_price,
            'nonce': nonce or self.w3.eth.get_transaction_count(from_address)
        }

        try:
            function = getattr(self.contracts[contract_name].functions, function_name)(*args)
            tx_hash = function.transact(tx_parameters)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            log_msg(f"Transaction {function_name} executed. From: {from_address}, Tx Hash: {tx_hash.hex()}, Gas: {gas}, Gas Price: {tx_parameters['gasPrice']}")
            return receipt

        except Exception as e:
            log_error(f"Error executing {function_name} from {from_address}. Error: {str(e)}")
            raise e

    def listen_to_event(self, contract_name):
        """
        Listens to a specific event from the smart contract indefinitely.

        Args:
            contract_name (str): The name of the contract to use.
        """
        event_filter = self.contracts[contract_name].events.ActionLogged.create_filter(fromBlock='latest')
        while True:
            entries = event_filter.get_new_entries()
            for event in entries:
                self.handle_action_logged(event)
            time.sleep(10)

    def handle_action_logged(self, event):
        """
        Handles events by logging a message when an event is caught.

        Args:
            event (dict): The event data returned by the blockchain.
        """
        log_msg(f"New Action Logged: {event['args']}")

    def register_entity(self, entity_type, *args, from_address, contract_name = 'SupplyChainRecords'):
        """
        Registers a new entity of a specified type in the contract.

        Args:
            entity_type (str): Type of the entity to register, e.g., 'certifier', 'carrier', 'farmer', 'producer', 'seller'.
            *args: Additional arguments required by the contract function.
            from_address (str): The Ethereum address to send the transaction from.
            contract_name (str): The name of the contract to use. Default is 'SupplyChainRecords'.

        Returns:
            The transaction receipt object.
        
        Raises:
            ValueError: If no function is available for the specified entity type or the from_address is invalid.
        """
        if not from_address:
            raise ValueError(Fore.RED + "A valid Ethereum address must be provided as 'from_address'." + Style.RESET_ALL)

        owner_address = self.contracts[contract_name].functions.getOwner().call()
        tx_hash = self.contracts[contract_name].functions.authorizeEditor(from_address).transact({'from': owner_address})
        self.w3.eth.wait_for_transaction_receipt(tx_hash)


        entity_functions = {
            'CARRIER': 'addCarrier',
            'CERTIFIER': 'addCertifier',
            'FARMER': 'addFarmer',
            'PRODUCER': 'addProducer',
            'SELLER': 'addSeller'
        }
        function_name = entity_functions.get(entity_type)
        if not function_name:
            raise ValueError(Fore.RED + f"No function available for entity type {entity_type}" + Style.RESET_ALL)
        return self.write_data(function_name, contract_name, from_address, *args)

    def update_entity(self, entity_type, *args, from_address, contract_name = 'SupplyChainRecords'):
        """
        Updates an existing entity of a specified type in the contract.

        Args:
            entity_type (str): Type of the entity to update.
            *args: Additional arguments required by the contract function.
            from_address (str): The Ethereum address to send the transaction from.
            contract_name (str): The name of the contract to use. Default is 'SupplyChainRecords'.

        Returns:
            The transaction receipt object.

        Raises:
            ValueError: If no function is available for the specified entity type or the from_address is invalid.
        """
        if not from_address:
            raise ValueError(Fore.RED + "A valid Ethereum address must be provided as 'from_address'." + Style.RESET_ALL)
        update_functions = {
            'CARRIER': 'updateCarrier',
            'CERTIFIER': 'updateCertifier',
            'FARMER': 'updateFarmer',
            'PRODUCER': 'updateProducer',
            'SELLER': 'updateSeller'
        }
        function_name = update_functions.get(entity_type)
        if not function_name:
            raise ValueError(Fore.RED + f"No function available for entity type {entity_type}" + Style.RESET_ALL)
        return self.write_data(function_name, contract_name, from_address, *args)

    def create_nft(self, *args, from_address, contract_name='SupplyChainNFT'):
        """
        Mints a new NFT by calling the mint function in the smart contract.

        Args:
            *args: Additional arguments required by the contract function.
            from_address (str): The Ethereum address to send the transaction from.
            contract_name (str): Name of the contract (default is 'SupplyChainNFT').

        Returns:
            dict: Transaction receipt.
    
        Raises:
            ValueError: If any required parameter is missing.
        """
        if not from_address:
            raise ValueError(Fore.RED + "A valid Ethereum address must be provided as 'from_address'." + Style.RESET_ALL)
        """if not to_address:
            raise ValueError(Fore.RED + "A valid recipient address ('to_address') must be provided." + Style.RESET_ALL)
        """
        owner_address = self.contracts[contract_name].functions.getOwner().call()
        tx_hash = self.contracts[contract_name].functions.authorizeEditor(from_address).transact({'from': owner_address})
        self.w3.eth.wait_for_transaction_receipt(tx_hash)

        return self.write_data("mint", contract_name, from_address, *args)

    def update_nft(self, *args, from_address, contract_name='SupplyChainNFT'):
        """
        Updates an existing NFT on the blockchain by calling the 'updateNFT' function
        in the SupplyChainNFT smart contract.

        Args:
            *args: Arguments required by the updateNFT function.
            from_address (str): The Ethereum address to send the transaction from.
            contract_name (str): Name of the smart contract (default is 'SupplyChainNFT').

        Returns:
            dict: Transaction receipt of the update operation.

        Raises:
            ValueError: If 'from_address' is not provided.
        """
        if not from_address:
            raise ValueError(Fore.RED + "A valid Ethereum address must be provided as 'from_address'." + Style.RESET_ALL)

        return self.write_data("updateNFT", contract_name, from_address, *args)

    def transfer_nft(self, token_id, to_address, nextRole, from_address, contract_name='SupplyChainNFT'):
        """
        Transfers an NFT from one address to another using the smart contract's custom logic.

        Args:
            to_address (str): The Ethereum address of the recipient.
            token_id (int): The ID of the NFT to be transferred.
            from_address (str): The Ethereum address of the current owner.
            contract_name (str): Name of the smart contract (default is 'SupplyChainNFT').

        Returns:
            dict: Transaction receipt of the transfer operation.

        Raises:
            ValueError: If any required parameter is missing.
        """
        if not from_address:
            raise ValueError(
                Fore.RED + "A valid Ethereum address must be provided as 'from_address'." + Style.RESET_ALL)
        if not to_address:
            raise ValueError(
                Fore.RED + "A valid recipient address ('to_address') must be provided." + Style.RESET_ALL)

        return self.write_data("safeTransferNFT", contract_name, from_address, token_id, to_address, nextRole)

    def get_nft_data_by_owner(self, owner_address, contract_name='SupplyChainNFT'):
        """
        Retrieves all NFTs owned by a specific user from the blockchain.
    
        Args:
            owner_address (str): The Ethereum address of the NFT owner.
            contract_name (str): Name of the smart contract (default is 'SupplyChainNFT').
    
        Returns:
            tuple: Contains six arrays (ids, names, categories, emissions, scores, harvests)
            representing all NFTs owned by the specified address.
        """
        return self.read_data("getNFTDataByOwner", contract_name, owner_address)

    def get_emissions_by_nft_id(self, nft_id, contract_name='SupplyChainNFT'):
        """
        Retrieves the emissions data for a specific NFT by its ID.
    
        Args:
            nft_id (int): The ID of the NFT.
            contract_name (str): Name of the smart contract (default is 'SupplyChainNFT').
    
        Returns:
            tuple: Contains emissions data for the specified NFT.
        """
        return self.read_data("getEmissionsByNFTId", contract_name, nft_id)

    def get_last_id(self, contract_name='SupplyChainNFT'):
        """
        Retrieves the last ID used for NFTs in the smart contract.
    
        Args:
            contract_name (str): Name of the smart contract (default is 'SupplyChainNFT').
    
        Returns:
            int: The last ID used for NFTs.
        """
        return self.read_data("getLastTokenId", contract_name)

    def assign_carbon_credits(self, *args, from_address, contract_name = 'CarbonCreditToken'):
        """
        Assigns carbon credits to a user.
        Args:
            *args: Additional arguments required by the contract function.
            from_address (str): The Ethereum address to send the transaction from.
            contract_name (str): The name of the contract to use. Default is 'CarbonCreditToken'.
        Returns:
            The transaction receipt object.
        """
        owner_address = self.contracts[contract_name].functions.getOwner().call()
        tx_hash = self.contracts[contract_name].functions.authorizeEditor(from_address).transact({'from': owner_address})
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return self.write_data('mint', contract_name, from_address, *args)

    def get_balance(self, user_key, contract_name='CarbonCreditToken'):
        """
        Retrieves the balance of carbon credits for a specific user.
    
        Args:
            user_key (str): The user's Ethereum address.
            contract_name (str): Name of the smart contract (default is 'CarbonCreditToken').
    
        Returns:
            user balance.
        """
        return self.read_data("balanceOf", contract_name, user_key)

    def transfer_carbon_credits(self, *args, from_address, contract_name = 'CarbonCreditToken'):
        """
        Transfers carbon credits from one user to another.
    
        Args:
            *args: Additional arguments required by the contract function.
            from_address (str): The Ethereum address to send the transaction from.
            contract_name (str): The name of the contract to use. Default is 'CarbonCreditToken'.
    
        Returns:
            The transaction receipt object.
        """
        owner_address = self.contracts[contract_name].functions.getOwner().call()
        tx_hash = self.contracts[contract_name].functions.authorizeEditor(from_address).transact({'from': owner_address})
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return self.write_data("transferCredits", contract_name, from_address, *args)

    def remove_carbon_credits(self, *args, from_address, contract_name = 'CarbonCreditToken'):
        """
        remove carbon credits to a user.
        Args:
            amount (int): The amount of carbon credits to remove.
            from_address (str): The Ethereum address to send the transaction from.
            contract_name (str): The name of the contract to use. Default is 'CarbonCreditToken'.
        Returns:
            The transaction receipt object.
        """
        owner_address = self.contracts[contract_name].functions.getOwner().call()
        tx_hash = self.contracts[contract_name].functions.authorizeEditor(from_address).transact({'from': owner_address})
        self.w3.eth.wait_for_transaction_receipt(tx_hash)

        return self.write_data('burn', contract_name, from_address, *args)