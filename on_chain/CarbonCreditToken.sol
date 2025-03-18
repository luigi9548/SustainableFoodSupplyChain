// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../node_modules/@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "../node_modules/@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title Carbon Credit Token
 * @dev ERC-20 token representing carbon credits that can be traded and burned for offsetting emissions.
 */
contract CarbonCreditToken is ERC20, Ownable{
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

    //Events for actions
    event CreditsMint(address to, uint256 amount);
    event CarbonCreditsBurned(address from, uint256 amount);
    event CarbonCreditsTransferred(address from, uint256 amount);
    event ActionLogged(uint256 indexed actionId, string actionType, address indexed initiator, uint256 indexed timestamp, string details);

    /**
     * @dev Initializes the Carbon Credit Token contract.
     */
    constructor() ERC20("Carbon Credit Token", "CCT") Ownable(msg.sender){}

    /**
     * @notice Allows verified issuers to mint new carbon credits.
     * @dev Only addresses marked as verified issuers can call this function.
     * @param to The address receiving the newly minted carbon credits.
     * @param amount The amount of carbon credits to mint.
     */
    function mint(address to, uint256 amount) external {
        require(verifiedIssuers[msg.sender], "Not authorized to mint");
        logAction("Mint", msg.sender, "New Carbon credit minted");
        _mint(to, amount);
    }

    /**
     * @notice Burns an amount of carbon credits from a specified address.
     * @param from Address from which to consume carbon credits.
     * @param amount Amount of carbon credits to burn.
     * @dev This function reduces the 'from' wallet balance and total supply.
     */
    function burn(address from, uint256 amount) public {
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
    function transferCredits(address to, uint256 amount) external {
        require(to != address(0), "Invalid recipient address");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");
        logAction("Transfer", msg.sender, "Carbon credits transferred");
        _transfer(msg.sender, to, amount);
    }


    /**
     * @notice Enables the contract owner to add or remove verified issuers.
     * @dev Only the contract owner can call this function.
     * @param issuer The address of the entity being added or removed.
     * @param status Boolean value indicating if the issuer is verified (true) or removed (false).
     */
    function setIssuer(address issuer, bool status) external onlyOwner {
        verifiedIssuers[issuer] = status;
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
