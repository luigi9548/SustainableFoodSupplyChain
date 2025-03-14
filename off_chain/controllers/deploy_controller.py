import os
import random
from colorama import Fore, Style, init
from web3 import Web3
from solcx import compile_standard, get_installed_solc_versions, install_solc

class DeployController:
    """
    DeployController handles initialization, compilation and deployment for Solidity contract, establishing 
    a connection with Ganache through Web3.
    """

    init(convert=True)

    def __init__(self, http_provider='http://ganache:8545', solc_version='0.8.0'):
        """
        Initializes the deployment controller with Ethereum HTTP provider and Solidity 
        compiler version.
        
        Args:
            http_provider (str): The HTTP URL to connect to an Ethereum node.
            solc_version (str): The version of the Solidity compiler to use for compiling contracts.
        """
        #http://ganache:8545
        #http://127.0.0.1:8545
        self.http_provider = http_provider
        self.solc_version = solc_version
        self.w3 = Web3(Web3.HTTPProvider(self.http_provider))
        assert self.w3.is_connected(), Fore.RED + "Failed to connect to Ethereum node." + Style.RESET_ALL
        self.contract = None

    def compile_and_deploy(self, contracts_source_dir, account=None):
        """
        Compiles and deploys all smart contracts in a given directory to an Ethereum network.

        Args:
            contracts_source_dir (str): Path to the Solidity contracts source directory.
            account (str): The Ethereum account to deploy from (randomly chosen if not provided).
        """
        # Resolve the full path of the contracts directory
        dir_path = os.path.dirname(os.path.realpath(__file__))
        shared_dir_path = os.path.dirname(os.path.dirname(dir_path))
        contracts_full_path = os.path.normpath(os.path.join(shared_dir_path, contracts_source_dir))

        # Ensure the directory exists
        if not os.path.isdir(contracts_full_path):
            raise FileNotFoundError(f"Contracts directory not found: {contracts_full_path}")

        # Iterate over all Solidity files in the directory
        for filename in os.listdir(contracts_full_path):
            if filename.endswith(".sol"):  # Only process Solidity files
                contract_path = os.path.join(contracts_full_path, filename)
            
                with open(contract_path, 'r') as file:
                    contract_source_code = file.read()

                # Compile and deploy the contract
                self.compile_contract(contract_source_code, filename)
                selected_account = account or random.choice(self.w3.eth.accounts)
                self.deploy_contract(selected_account)

    def compile_contract(self, solidity_source, contract_filename):
        """
        Compiles a Solidity contract using the specified version of solc.
    
        Args:
            solidity_source (str): The source code of the Solidity contract.
            contract_filename (str): The filename of the Solidity contract.
        """
        # Install solc version if not already installed
        if self.solc_version not in get_installed_solc_versions():
            install_solc(self.solc_version)

        # Compile the Solidity source code
        compiled_sol = compile_standard({
            "language": "Solidity",
            "sources": {f"on_chain/{contract_filename}": {"content": solidity_source}},
            "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}}
        }, solc_version=self.solc_version)

        # Extract the ABI and bytecode
        self.contract_id, self.contract_interface = next(iter(compiled_sol['contracts'][f'on_chain/{contract_filename}'].items()))
        self.abi = self.contract_interface['abi']
        self.bytecode = self.contract_interface['evm']['bytecode']['object']

    def deploy_contract(self, account):
        """
        Deploys the compiled contract using the provided account.
        
        Args:
            account (str): The account to deploy the contract from.
        """
        try:
            # Create the contract in Web3
            contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)

             # Send transaction to deploy the contract
            tx_hash = contract.constructor().transact({'from': account})
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            self.contract = self.w3.eth.contract(address=tx_receipt.contractAddress, abi=self.abi)
            print(f'Contract deployed at {tx_receipt.contractAddress} from {account}')
        except Exception as e:
            print(Fore.RED + f"An error occurred while deploying the contract from account {account}: {e}" + Style.RESET_ALL)