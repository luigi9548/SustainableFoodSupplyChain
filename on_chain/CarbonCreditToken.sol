// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../node_modules/@openzeppelin/contracts/token/ERC20/ERC20.sol";

/**
 * @title Carbon Credit Token
 * @dev ERC-20 token representing carbon credits that can be traded and burned for offsetting emissions.
 */
contract CarbonCreditToken is ERC20{
    //Struct to log actions for every previous struct
    struct ActionLog {
        uint256 actionId;
        string actionType;
        address initiatedBy;
        uint256 timestamp;
        string details;
    }

    //State variables and mapping
    uint256 private actionCounter = 0;
    mapping(address => bool) public verifiedIssuers;
    mapping(uint256 => ActionLog) public actionLogs;
    mapping(address => bool) public authorizedEditors;
    address public owner;

    //Events for actions
    event CreditsMint(address to, uint256 amount);
    event CarbonCreditsBurned(address from, uint256 amount);
    event CarbonCreditsTransferred(address from, uint256 amount);
    event ActionLogged(uint256 indexed actionId, string actionType, address indexed initiator, uint256 indexed timestamp, string details);

    /**
     * @dev Initializes the Carbon Credit Token contract.
     */
    constructor() ERC20("Carbon Credit Token", "CCT")
    {
        owner = msg.sender;
        authorizedEditors[owner] = true;
    }

    //Modifiers
    /**
     * @dev Restricts function access to the contract owner only.
     */
    modifier onlyOwner() {
        require(msg.sender == owner, "This function is restricted to the contract owner.");
        _;
    }

    /**
     * @dev Restricts function access to either the contract owner or authorized editors.
     */
    modifier onlyAuthorized() {
        require(msg.sender == owner || authorizedEditors[msg.sender], "Access denied: caller is not the owner or an authorized editor.");
        _;
    }
    
    /**
     * @dev Return Owner Account.
     */
    function getOwner() public view returns (address) {
        return owner;
    }


    // Functions
    /**
     * @dev Authorizes a new editor to manage records.
     * @param _editor Address of the new editor to authorize.
     */
    function authorizeEditor(address _editor) public onlyOwner {
        authorizedEditors[_editor] = true;
    }

    /**
     * @notice Allows verified issuers to mint new carbon credits.
     * @dev Only addresses marked as verified issuers can call this function.
     * @param to The address receiving the newly minted carbon credits.
     * @param amount The amount of carbon credits to mint.
     */
    function mint(address to, uint256 amount)  public onlyAuthorized {
        logAction("Mint", msg.sender, "New Carbon credit minted");
        _mint(to, amount);
        emit CreditsMint(to, amount);
    }

    /**
     * @notice Burns an amount of carbon credits from a specified address.
     * @param from Address from which to consume carbon credits.
     * @param amount Amount of carbon credits to burn.
     * @dev This function reduces the 'from' wallet balance and total supply.
     */
    function burn(address from, uint256 amount) public onlyAuthorized{
        require(balanceOf(from) >= amount, "Insufficient balance to burn");
        _burn(from, amount);
        logAction("Burn", msg.sender, "Carbon credits burned");
        emit CarbonCreditsBurned(from, amount);
    }

    /**
    * @notice Transfers carbon credits between supply chain actors
    * @dev Allows any actor to send carbon credits to another actor
    * @param to Recipient address
    * @param amount Amount of carbon credits to transfer
    */
    function transferCredits(address to, uint256 amount) public onlyAuthorized {
        require(to != address(0), "Invalid recipient address");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");
        logAction("Transfer", msg.sender, "Carbon credits transferred");
        _transfer(msg.sender, to, amount);
        emit CarbonCreditsTransferred(to, amount);
    }

    /**
     * @dev Logs actions taken by users within the system for auditing purposes.
     * @param _actionType Type of action performed.
     * @param _initiator Address of the user who initiated the action.
     * @param _details Details or description of the action.
     */
    function logAction(string memory _actionType, address _initiator, string memory _details) internal {
        actionCounter++;
        actionLogs[actionCounter] = ActionLog(actionCounter, _actionType, _initiator, block.timestamp, _details);
        emit ActionLogged(actionCounter, _actionType, _initiator, block.timestamp, _details);
    }
}
