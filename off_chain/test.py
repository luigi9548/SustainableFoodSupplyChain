import pytest
from unittest.mock import patch, MagicMock
from cli.cli import CommandLineInterface
from session.session import Session

@pytest.fixture
def cli():
    session = MagicMock(spec=Session)
    cli_instance = CommandLineInterface(session)
    mock_web3 = MagicMock()
    mock_web3.is_connected.return_value = True
    return cli_instance

def test_successful_registration(cli):
    with patch('builtins.input', side_effect=[
        '0xbb38Fd54323Bb55b3Eb38497076f8d80AF11bF77',                        # Public key input
        'username',                                                          # Username input
        'F', 'Y',                                                            # Role = Farmer and confirm
        'Password123!', 'Password123!',                                      # Password and confirmation
        '0x25f460c4f7848fca91b4c6334a4ad39707cb829e84a1df9243d01ad3b4c6df1d', 
        '0x25f460c4f7848fca91b4c6334a4ad39707cb829e84a1df9243d01ad3b4c6df1d' # Private key and confirmation
    ]), patch('maskpass.askpass', side_effect=[
        '0x25f460c4f7848fca91b4c6334a4ad39707cb829e84a1df9243d01ad3b4c6df1d', 
        '0x25f460c4f7848fca91b4c6334a4ad39707cb829e84a1df9243d01ad3b4c6df1d',# Private key e conferma
        'Password123!', 'Password123!',                                      # Password e conferma
        '0x25f460c4f7848fca91b4c6334a4ad39707cb829e84a1df9243d01ad3b4c6df1d', 
        '0x25f460c4f7848fca91b4c6334a4ad39707cb829e84a1df9243d01ad3b4c6df1d' # Private key e conferma
    ]), patch.object(cli.controller, 'check_keys', return_value=False), \
         patch.object(cli.controller, 'check_username', return_value=0), \
         patch.object(cli.controller, 'registration', return_value=0), \
         patch.object(cli, 'insert_actor_info', return_value=None), \
         patch.object(cli.act_controller, 'deploy_and_initialize'), \
         patch('eth_utils.is_address', return_value=True), \
         patch('eth_keys.keys.PrivateKey') as mock_private_key:

        mock_private_key.return_value.public_key.to_checksum_address.return_value = '0xbb38Fd54323Bb55b3Eb38497076f8d80AF11bF77'
        cli.registration_menu()

def test_successful_login(cli):
    with patch('builtins.input', side_effect=[
        'username',          # Username input
    ]), patch('maskpass.askpass', return_value='Password123!'), \
         patch.object(cli.controller, 'check_attempts', return_value=True), \
         patch.object(cli.session, 'get_timeout_left', return_value=0), \
         patch.object(cli.controller, 'login', return_value=(1, 'FARMER')), \
         patch.object(cli, 'common_menu_options', return_value=None):

        cli.login_menu()

def test_certifier_menu_view_profile(cli):
    with patch('builtins.input', side_effect=[
        '9', '13', 'Y'  # View profile -> Logout -> Confirm logout
    ]), patch.object(cli.util, 'view_userView'), \
         patch.object(cli.session, 'reset_session'):

        cli.certifier_menu('certifier_user')

def test_common_menu_options_view_profile(cli):
    with patch('builtins.input', side_effect=[
        '1', '11', 'Y'  # View profile -> Logout -> Confirm logout
    ]), patch.object(cli.util, 'view_userView'), \
         patch.object(cli.session, 'reset_session'):

        cli.common_menu_options('FARMER', 'farmer_user')
