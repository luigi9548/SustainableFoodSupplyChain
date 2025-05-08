// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../node_modules/@openzeppelin/contracts/token/ERC721/ERC721.sol";


/**
 * @title SupplyChainNFT
 * @dev ERC721 contract to manage NFTs representing food products in the supply chain
 */
contract SupplyChainNFT is ERC721 {
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
    mapping(address => bool) public authorizedEditors;
    address public owner;
   
    //Events for actions
    event NFTTransferred(uint256 indexed tokenId, address indexed from, address indexed to, string newRole);
    event NFTUpdated(uint256 indexed tokenId, string name, uint256 emissions);
    event NFTMint(address to, string role, string name);
    event ActionLogged(uint256 indexed actionId, string actionType, address indexed initiator, uint256 indexed timestamp, string details);

    /**
     * @dev Constructor to initialize the ERC721 token
     */
    constructor() ERC721("SupplyChainNFT", "SCNFT") {
        owner = msg.sender;
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
    function mint(address to, string memory role, string memory name, string memory category, uint256 emissions, uint256 qualityScore, uint256 harvestDate) external onlyAuthorized {
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
    function safeTransferNFT(uint256 tokenId, address to, string memory nextRole) public {
        require(ownerOf(tokenId) == msg.sender, "Not the owner of the NFT");
        string memory currentRole = nfts[tokenId].role;
                
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
        if (keccak256(bytes(fromRole)) == keccak256(bytes("FARMER")) && keccak256(bytes(toRole)) == keccak256(bytes("CARRIER"))) return true;
        if (keccak256(bytes(fromRole)) == keccak256(bytes("CARRIER")) && keccak256(bytes(toRole)) == keccak256(bytes("PRODUCER"))) return true;
        if (keccak256(bytes(fromRole)) == keccak256(bytes("PRODUCER")) && keccak256(bytes(toRole)) == keccak256(bytes("CARRIER"))) return true;
        if (keccak256(bytes(fromRole)) == keccak256(bytes("CARRIER")) && keccak256(bytes(toRole)) == keccak256(bytes("SELLER"))) return true;
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

    /**
     * @notice Returns all NFTs owned by a specific user
     * @param user Address of the user
     * @return ids The list of NFT IDs owned by the user
     * @return names The list of NFT names owned by the user
     * @return categories The list of NFT categories owned by the user
     * @return emissions The list of CO2 emissions of NFTs owned by the user
     * @return scores The list of quality scores of NFTs owned by the user
     * @return harvests The list of harvest dates of NFTs owned by the user
     */
    function getNFTDataByOwner(address user) public view returns (
        uint256[] memory ids,
        string[] memory names,
        string[] memory categories,
        uint256[] memory emissions,
        uint256[] memory scores,
        uint256[] memory harvests
    ) {
        uint256 total = nextTokenId;
        uint256 count = 0;

        // Conta quanti NFT possiede
        for (uint256 i = 0; i < total; i++) {
            if (ownerOf(i) == user) {
                count++;
            }
        }

        // Prepara array per ogni campo della struct
        ids = new uint256[](count);
        names = new string[](count);
        categories = new string[](count);
        emissions = new uint256[](count);
        scores = new uint256[](count);
        harvests = new uint256[](count);

        uint256 index = 0;
        for (uint256 i = 0; i < total; i++) {
            if (ownerOf(i) == user) {
                NFT memory nft = nfts[i];
                ids[index] = nft.id;
                names[index] = nft.name;
                categories[index] = nft.category;
                emissions[index] = nft.co2Emission;
                scores[index] = nft.qualityScore;
                harvests[index] = nft.harvestDate;
                index++;
            }
        }
        return (ids, names, categories, emissions, scores, harvests);
    }

    /**
     * @notice Retrieves the CO2 emissions for a specific NFT based on its ID
     * @param tokenId ID of the NFT
     * @return emissions The CO2 emissions (in Kg) associated with the NFT
     */
    function getEmissionsByNFTId(uint256 tokenId) public view returns (uint256 emissions) {
        // Verifica se l'NFT esiste usando la funzione ownerOf
        address owner = ownerOf(tokenId);
        require(owner != address(0), "NFT does not exist");

        // Restituisce le emissioni di CO2 dell'NFT
        emissions = nfts[tokenId].co2Emission;
    }

    // Funzione per ottenere l'ultimo tokenId emesso
    function getLastTokenId() public view returns (uint256) {
        return nextTokenId - 1;
    }

}