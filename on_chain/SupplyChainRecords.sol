// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

//Documentation for this contract written in NatSpec format
/**
 * @title Supply Chain Records System
 * @dev Manages supplychain records for certifiers, farmers, carriers, producers and sellers.
 * @notice This contract is intended for demonstration purposes and not for production use.
 */

 contract SuuplyChainRecords {

    // Declaration of carbon credit
    //ICarbonCreditToken public carbonCreditToken;

	 // Structs for every type of user
	struct Certifier {
        string name;
        string lastName;
        bool isRegistered;
    }

    struct Farmer {
        string name;
        string lastName;
        bool isRegistered;
    }

    struct Carrier {
        string name;
        string lastName;
        bool isRegistered;
    }

    struct Producer {
        string name;
        string lastName;
        bool isRegistered;
    }

    struct Seller {
        string name;
        string lastName;
        bool isRegistered;
    }

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
    mapping(address  => Certifier) public certifiers;
    mapping(address  => Producer) public producers;
    mapping(address  => Carrier) public carriers;
    mapping(address => Farmer) public farmers;
    mapping(address => Seller) public sellers;
    mapping(uint256 => ActionLog) public actionLogs;
    mapping(address => bool) public authorizedEditors;
    address public owner;

    //Events for actions
    event EntityRegistered(string entityType, address indexed entityAddress);
    event EntityUpdated(string entityType, address indexed entityAddress);
    event ActionLogged(uint256 indexed actionId, string actionType, address indexed initiator, uint256 indexed timestamp, string details);

    /**
     * @dev Sets the contract owner as the deployer and initializes authorized editors.
     */
    constructor() {
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

    /**
     * @dev Add a new certifier record to the system.
     * @param name First name of the certifier.
     * @param lastName Last name of the certifier.
     * @notice Only authorized users can add certifier records.
     */
    function addCertifier(string memory name, string memory lastName) public onlyAuthorized {
        require(!certifiers[msg.sender].isRegistered, "Certifier already registered");
        Certifier storage certifier = certifiers[msg.sender];
        certifier.name = name;
        certifier.lastName = lastName;
        certifier.isRegistered = true;
        logAction("Create", msg.sender, "Certifier added");
        emit EntityRegistered("Certifier", msg.sender);
    }

    /**
     * @dev Updates existing certifier information.
     * @param name Updated first name of the certifier.
     * @param lastName Updated last name of the certifier.
     * @notice Only authorized users can update certifier records.
     */
    function updateCertifier(string memory name, string memory lastName) public onlyAuthorized {
        require(certifiers[msg.sender].isRegistered, "Certifier not found");
        Certifier storage certifier = certifiers[msg.sender];
        certifier.name = name;
        certifier.lastName = lastName;
        logAction("Update", msg.sender, "Certifier updated");
        emit EntityUpdated("Certifier", msg.sender);
    }

    /**
     * @dev Add a new farmer record to the system.
     * @param name First name of the farmer.
     * @param lastName Last name of the farmer.
     * @notice Only authorized users can add farmer records.
     */
    function addFarmer(string memory name, string memory lastName) public onlyAuthorized {
        require(!farmers[msg.sender].isRegistered, "Farmer already registered");
        Farmer storage farmer = farmers[msg.sender];
        farmer.name = name;
        farmer.lastName = lastName;
        farmer.isRegistered = true;
        logAction("Create", msg.sender, "Farmer added");
        emit EntityRegistered("Farmer", msg.sender);
    }

    /**
     * @dev Updates existing certifier information.
     * @param name Updated first name of the certifier.
     * @param lastName Updated last name of the certifier.
     * @notice Only authorized users can update certifier records.
     */
    function updateFarmer(string memory name, string memory lastName) public onlyAuthorized {
        require(farmers[msg.sender].isRegistered, "Farmer not found");
        Farmer storage farmer = farmers[msg.sender];
        farmer.name = name;
        farmer.lastName = lastName;
        logAction("Update", msg.sender, "Farmer updated");
        emit EntityUpdated("Farmer", msg.sender);
    }

    /**
     * @dev Add a new carrier record to the system.
     * @param name First name of the carrier.
     * @param lastName Last name of the carrier.
     * @notice Only authorized users can add carrier records.
     */
    function addCarrier(string memory name, string memory lastName) public onlyAuthorized {
        require(!carriers[msg.sender].isRegistered, "Carrier already registered");
        Carrier storage carrier = carriers[msg.sender];
        carrier.name = name;
        carrier.lastName = lastName;
        carrier.isRegistered = true;
        logAction("Create", msg.sender, "Carrier added");
        emit EntityRegistered("Carrier", msg.sender);
    }

    /**
     * @dev Updates existing carrier information.
     * @param name Updated first name of the carrier.
     * @param lastName Updated last name of the carrier.
     * @notice Only authorized users can update carrier records.
     */
    function updateCarrier(string memory name, string memory lastName) public onlyAuthorized {
        require(carriers[msg.sender].isRegistered, "Carrier not found");
        Carrier storage carrier = carriers[msg.sender];
        carrier.name = name;
        carrier.lastName = lastName;
        logAction("Update", msg.sender, "Carrier updated");
        emit EntityUpdated("Carrier", msg.sender);
    }

    /**
     * @dev Add a new producer record to the system.
     * @param name First name of the producer.
     * @param lastName Last name of the producer.
     * @notice Only authorized users can add producer records.
     */
    function addProducer(string memory name, string memory lastName) public onlyAuthorized {
        require(!producers[msg.sender].isRegistered, "Producer already registered");
        Producer storage producer = producers[msg.sender];
        producer.name = name;
        producer.lastName = lastName;
        producer.isRegistered = true;
        logAction("Create", msg.sender, "Producer added");
        emit EntityRegistered("Producer", msg.sender);
    }

    /**
     * @dev Updates existing producer information.
     * @param name Updated first name of the producer.
     * @param lastName Updated last name of the producer.
     * @notice Only authorized users can update producer records.
     */
    function updateProducer(string memory name, string memory lastName) public onlyAuthorized {
        require(producers[msg.sender].isRegistered, "Producer not found");
        Producer storage producer = producers[msg.sender];
        producer.name = name;
        producer.lastName = lastName;
        logAction("Update", msg.sender, "Producer updated");
        emit EntityUpdated("Producer", msg.sender);
    }


    /**
     * @dev Add a new seller record to the system.
     * @param name First name of the seller.
     * @param lastName Last name of the seller.
     * @notice Only authorized users can add seller records.
     */
    function addSeller(string memory name, string memory lastName) public onlyAuthorized {
        require(!sellers[msg.sender].isRegistered, "Seller already registered");
        Seller storage seller = sellers[msg.sender];
        seller.name = name;
        seller.lastName = lastName;
        seller.isRegistered = true;
        logAction("Create", msg.sender, "Seller added");
        emit EntityRegistered("Seller", msg.sender);
    }

    /**
     * @dev Updates existing seller information.
     * @param name Updated first name of the seller.
     * @param lastName Updated last name of the seller.
     * @notice Only authorized users can update seller records.
     */
    function updateSeller(string memory name, string memory lastName) public onlyAuthorized {
        require(sellers[msg.sender].isRegistered, "Seller not found");
        Seller storage seller = sellers[msg.sender];
        seller.name = name;
        seller.lastName = lastName;
        logAction("Update", msg.sender, "Seller updated");
        emit EntityUpdated("Seller", msg.sender);
    }
 }