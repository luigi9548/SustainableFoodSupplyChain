// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../node_modules/@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "../node_modules/@openzeppelin/contracts/access/Ownable.sol";


/**
 * @title SupplyChainNFT
 * @dev ERC721 contract to manage NFTs representing food products in the supply chain
 */
contract SupplyChainNFT is ERC721, Ownable {
    /**
     * @dev Structure representing an NFT in the supply chain
     * @param id Unique identifier of the NFT
     * @param owner Current owner of the NFT
     * @param role Role of the owner in the supply chain (Farmer, Carrier, Producer, Seller)
     * @param name Name of the product associated with the NFT
     * @param category // Category of the product (e.g., fruit, meat, dairy)
     * @param co2Emission // CO₂ emissions in Kg
     * @param qualityScore // Quality score of the product
     * @param harvestDate // Harvest or production date (Unix timestamp)
     */
    struct NFT {
        uint256 id;
        address owner;
        string role;
        string name;
        string category;
        uint256 co2Emission;
        uint256 qualityScore;
        uint256 harvestDate;
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
    uint256 private nextTokenId;
    mapping(uint256 => NFT) public nfts;
    mapping(address => string) public userRoles;
    mapping(uint256 => ActionLog) public actionLogs;
    
    //Events for actions
    event NFTTransferred(uint256 indexed tokenId, address indexed from, address indexed to, string newRole);
    event NFTUpdated(uint256 indexed tokenId, string name, uint256 emissions);
    event NFTMint(address to, string role, string name);
    event ActionLogged(uint256 indexed actionId, string actionType, address indexed initiator, uint256 indexed timestamp, string details);

    /**
     * @dev Constructor to initialize the ERC721 token
     */
    constructor() ERC721("SupplyChainNFT", "SCNFT") Ownable(msg.sender) {}

    /**
     * @notice Mints a new NFT and assigns it to a specified address
     * @dev Only the contract owner can mint new NFTs
     * @param to Address receiving the NFT
     * @param role Role of the receiver in the supply chain
     * @param name Name of the product
     * @param category // Category of the product (e.g., fruit, meat, dairy)
     * @param emissions Carbon emissions of the product
     * @param qualityScore // Quality score of the product
     * @param harvestDate // Harvest or production date (Unix timestamp)
     */
    function mint(address to, string memory role, string memory name, string memory category, uint256 emissions, uint256 qualityScore, uint256 harvestDate) external onlyOwner {
        uint256 tokenId = nextTokenId++;
        _safeMint(to, tokenId);
        nfts[tokenId] = NFT(tokenId, to, role, name, category, emissions, qualityScore, harvestDate);
        userRoles[to] = role;

        logAction("Mint", msg.sender, "New NFT minted");
        emit NFTMint(to, role, name);
    }

    /**
     * @notice Transfers an NFT while enforcing the supply chain sequence
     * @dev Ensures the transfer follows the Farmer → Carrier → Producer → Carrier → Seller rule
     * @param tokenId ID of the NFT to be transferred
     * @param to Address of the new owner
     */
    function safeTransferNFT(uint256 tokenId, address to) public {
        require(ownerOf(tokenId) == msg.sender, "Not the owner of the NFT");
        string memory currentRole = nfts[tokenId].role;
        string memory nextRole = userRoles[to];

        require(isValidTransfer(currentRole, nextRole), "Invalid transfer direction");

        _transfer(msg.sender, to, tokenId);
        nfts[tokenId].owner = to;
        nfts[tokenId].role = nextRole;

        logAction("NFT transfer", msg.sender, "NFT transferred");
        emit NFTTransferred(tokenId, msg.sender, to, nextRole);
    }

    /**
     * @notice Validates whether an NFT transfer follows the correct supply chain sequence
     * @param fromRole Current owner's role
     * @param toRole New owner's role
     * @return bool Returns true if the transfer is valid, false otherwise
     */
    function isValidTransfer(string memory fromRole, string memory toRole) internal pure returns (bool) {
        if (keccak256(bytes(fromRole)) == keccak256(bytes("Farmer")) && keccak256(bytes(toRole)) == keccak256(bytes("Carrier"))) return true;
        if (keccak256(bytes(fromRole)) == keccak256(bytes("Carrier")) && keccak256(bytes(toRole)) == keccak256(bytes("Producer"))) return true;
        if (keccak256(bytes(fromRole)) == keccak256(bytes("Producer")) && keccak256(bytes(toRole)) == keccak256(bytes("Carrier"))) return true;
        if (keccak256(bytes(fromRole)) == keccak256(bytes("Carrier")) && keccak256(bytes(toRole)) == keccak256(bytes("Seller"))) return true;
        return false;
    }

    /**
     * @notice Assigns a role to a user in the supply chain
     * @dev Only the contract owner can assign roles
     * @param user Address of the user
     * @param role Role to be assigned (Farmer, Carrier, Producer, Seller)
     */
    function setUserRole(address user, string memory role) external onlyOwner {
        userRoles[user] = role;
    }

    /**
     * @notice Updates the information of an existing NFT
     * @dev Only the NFT owner can update its details
     * @param tokenId ID of the NFT to update
     * @param emissions New carbon emissions value
     */
    function updateNFT(uint256 tokenId, uint256 emissions) external {
        require(ownerOf(tokenId) == msg.sender, "Not the owner of the NFT");
        nfts[tokenId].co2Emission += emissions;

        logAction("Update ", msg.sender, " NFT transferred");
        emit NFTUpdated(tokenId, nfts[tokenId].name, emissions);
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