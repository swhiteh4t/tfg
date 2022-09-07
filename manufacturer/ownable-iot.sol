///SPDX-License-Identifier: IMSE

pragma solidity ^0.8.15;

import "./SmartNFT_Interface.sol";
import "./ERC721_Interface.sol";

contract OwnableIoT is ERC721, smartNFT {
    enum States {
        waitingForOwner,
        engagedWithOwner
    }

    address manufacturer; //Address of manufacturer and owner of Smart Contract
    uint256 tokenCounter; //To give a genuine tokenID based on the number of tokens created
    mapping(uint256 => address) ownerOfSD; //To khow who is the owner of a specific owner
    mapping(address => uint256) tokenIDOfBCA; //To khow which is the tokenID associated to a secure device
    mapping(address => uint256) ownerBalance; //To know how many tokens an owner has

    struct Token_Struct {
        address approved; //Indicate who can transfer this token, 0 if no one
        address SD; //Indicate the BCA of the secure device associated to this token
        States state; //If blocked (false) then token should be verified by new user or new owner
        uint256 hashK_OD; //Hash of the Key shared between owner and device
        uint256 hashK_UD; //Hash of the Key shared between user and device
        string dataEngagement; //Public Key to create K_OD or K_UD depending on token state
        string tokenAddress;
        uint256 digest; //Signature of the certificate
        uint256 timestamp; //Last time that device updated its proof of live
        uint256 timeout; //Maximun key age
    }

    Token_Struct[] Secure_Token;

    constructor() {
        manufacturer = msg.sender;
        tokenCounter = 1;
        Secure_Token.push(
            Token_Struct(
                address(0),
                address(0),
                States.waitingForOwner,
                0,
                0,
                "",
                "",
                0,
                0,
                0
            )
        );
    }

    function createToken(address _addressSD, address _addressOwner)
        public
        virtual
        override
        returns (uint256)
    {
        //Check if the sender of message is the manufacturer
        require(manufacturer == msg.sender);
        //Check if the Blockchain Account of the secure device is in the SmartContract
        if (tokenFromBCA(_addressSD) == 0) {
            //Create a new token
            Secure_Token.push(
                Token_Struct(
                    address(0),
                    _addressSD,
                    States.waitingForOwner,
                    0,
                    0,
                    "",
                    "",
                    0,
                    block.timestamp,
                    86400
                )
            );
            //Assigning a new tokenId
            uint256 _tokenId = tokenCounter++;
            tokenIDOfBCA[_addressSD] = _tokenId;
            //Assigning the owner
            ownerOfSD[_tokenId] = _addressOwner;
            ownerBalance[_addressOwner]++;
            //Return tokenId obtained
            return (_tokenId);
        } else {
            //If the BCA already exists then return the _tokenId
            return (tokenFromBCA(_addressSD));
        }
    }

    function startOwnerEngagement(
        uint256 _tokenId,
        string memory _dataEngagement,
        uint256 _hashK_O
    ) public virtual override {
        //Check if sender is the Owner of token and the State of token
        require(ownerOfSD[_tokenId] == msg.sender);
        if (
            (Secure_Token[_tokenId].timestamp +
                Secure_Token[_tokenId].timeout) > block.timestamp
        ) {
            Secure_Token[_tokenId].dataEngagement = _dataEngagement;
            Secure_Token[_tokenId].hashK_OD = _hashK_O;
        } else {
            emit TimeoutAlarm(_tokenId);
        }
    }

    function ownerEngagement(uint256 _hashK_D) public virtual override {
        uint256 _tokenId = tokenFromBCA(msg.sender);
        //Check if public key owner-device exists from tokenID of BCA sender
        bytes memory emptyString = bytes(Secure_Token[_tokenId].dataEngagement);
        require(emptyString.length != 0, "Empty string");
        require(Secure_Token[_tokenId].hashK_OD == _hashK_D);
        require(Secure_Token[_tokenId].state == States.waitingForOwner);
        //Erase PK_Owner-Device and update timestamp
        Secure_Token[_tokenId].dataEngagement = "";
        Secure_Token[_tokenId].timestamp = block.timestamp;
        //Update the state of token
        Secure_Token[_tokenId].state = States.engagedWithOwner;
        //Send a notification to owner and device
        emit OwnerEngaged(_tokenId);
    }

    function tokenFromBCA(address _addressSD)
        public
        view
        virtual
        override
        returns (uint256)
    {
        return (tokenIDOfBCA[_addressSD]);
    }

    function ownerOfFromBCA(address _addressSD)
        public
        view
        virtual
        override
        returns (address)
    {
        return (ownerOfSD[tokenIDOfBCA[_addressSD]]);
    }

    function setTokenStorage(address _addressSD, string memory _tokenStorage)
        external
        override
    {
        require(msg.sender == ownerOfSD[tokenIDOfBCA[_addressSD]]);
        Secure_Token[tokenIDOfBCA[_addressSD]].tokenAddress = _tokenStorage;
    }

    function getTokenStorage(address _addressSD)
        external
        view
        returns (string memory)
    {
        return Secure_Token[tokenIDOfBCA[_addressSD]].tokenAddress;
    }

    function setCertificateDigest(address _addressSD, uint256 _certDigest)
        external
        override
    {
        require(msg.sender == ownerOfSD[tokenIDOfBCA[_addressSD]]);
        Secure_Token[tokenIDOfBCA[_addressSD]].digest = _certDigest;
    }

    function getCertificateDigest(address _addressSD)
        external
        view
        returns (uint256)
    {
        return Secure_Token[tokenIDOfBCA[_addressSD]].digest;
    }

    function resetKeyExchange(address _addressSD) external {
        require(msg.sender == ownerOfSD[tokenIDOfBCA[_addressSD]]);
        Secure_Token[tokenIDOfBCA[_addressSD]].digest = 0;
        Secure_Token[tokenIDOfBCA[_addressSD]].dataEngagement = "";
        Secure_Token[tokenIDOfBCA[_addressSD]].state = States.waitingForOwner;
    }

    function getDataEngagement(address _addressSD)
        external
        view
        returns (string memory)
    {
        return Secure_Token[tokenIDOfBCA[_addressSD]].dataEngagement;
    }

    function getInfoToken(uint256 _tokenId)
        public
        view
        returns (
            address _BCA_OWNER,
            address _BCA_SD,
            uint8 _state
        )
    {
        _BCA_OWNER = ownerOfSD[_tokenId];
        _BCA_SD = Secure_Token[_tokenId].SD;
        if (Secure_Token[_tokenId].state == States.waitingForOwner) {
            _state = 0;
        } else if (Secure_Token[_tokenId].state == States.engagedWithOwner) {
            _state = 1;
        } else {
            _state = 2;
        }
    }

    function getInfoTokenFromBCA(address _addressSD)
        public
        view
        returns (
            address _BCA_OWNER,
            uint256 _tokenId,
            uint8 _state
        )
    {
        _tokenId = tokenIDOfBCA[_addressSD];
        _BCA_OWNER = ownerOfSD[_tokenId];
        if (Secure_Token[_tokenId].state == States.waitingForOwner) {
            _state = 0;
        } else if (Secure_Token[_tokenId].state == States.engagedWithOwner) {
            _state = 1;
        } else {
            _state = 2;
        }
    }

    function balanceOf(address _owner)
        public
        view
        virtual
        override
        returns (uint256)
    {
        return (ownerBalance[_owner]);
    }

    function ownerOf(uint256 _tokenId)
        public
        view
        virtual
        override
        returns (address)
    {
        return (ownerOfSD[_tokenId]);
    }

    function safeTransferFrom(
        address _from,
        address _to,
        uint256 _tokenId,
        bytes memory data
    ) public payable virtual override {}

    function safeTransferFrom(
        address _from,
        address _to,
        uint256 _tokenId
    ) public payable virtual override {
        transferFrom(_from, _to, _tokenId);
    }

    function transferFrom(
        address _from,
        address _to,
        uint256 _tokenId
    ) public payable virtual override {
        require(
            (ownerOfSD[_tokenId] == msg.sender) ||
                (Secure_Token[_tokenId].approved == msg.sender)
        );
        require(ownerOfSD[_tokenId] == _from);
        if (
            (Secure_Token[_tokenId].timestamp +
                Secure_Token[_tokenId].timeout) > block.timestamp
        ) {
            ownerOfSD[_tokenId] = _to;
            ownerBalance[_from]--;
            ownerBalance[_to]++;
            //Secure_Token[_tokenId].approved = address(0);
            Secure_Token[_tokenId].state = States.waitingForOwner;
            //Erase old key exchange data between device with old Owner
            Secure_Token[_tokenId].dataEngagement = "";
            Secure_Token[_tokenId].hashK_UD = 0;
            Secure_Token[_tokenId].hashK_OD = 0;
            emit Transfer(_from, _to, _tokenId);
        } else {
            emit TimeoutAlarm(_tokenId);
        }
    }

    function approve(address _approved, uint256 _tokenId)
        public
        payable
        virtual
        override
    {}

    function setApprovalForAll(address _operator, bool _approved)
        public
        virtual
        override
    {}

    function getApproved(uint256 _tokenId)
        public
        view
        virtual
        override
        returns (address)
    {}

    function isApprovedForAll(address _owner, address _operator)
        public
        view
        virtual
        override
        returns (bool)
    {}

    function checkTimeout(uint256 _tokenId)
        public
        virtual
        override
        returns (bool)
    {
        require(ownerOfSD[_tokenId] == msg.sender);
        if (
            (Secure_Token[_tokenId].timestamp +
                Secure_Token[_tokenId].timeout) > block.timestamp
        ) {
            return true;
        } else {
            emit TimeoutAlarm(_tokenId);
            return false;
        }
    }

    function updateTimestamp() public virtual override {
        Secure_Token[tokenFromBCA(msg.sender)].timestamp = block.timestamp;
    }

    function setTimeout(uint256 _tokenId, uint256 _timeout)
        public
        virtual
        override
    {
        require(ownerOfSD[_tokenId] == msg.sender);
        Secure_Token[_tokenId].timeout = _timeout;
    }
}
