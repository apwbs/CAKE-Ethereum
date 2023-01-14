// SPDX-License-Identifier: CC-BY-SA-4.0
pragma solidity >= 0.5.0 < 0.9.0;

contract CAKEContract {

  struct userAttributes {
    bytes32 hashPart1;
    bytes32 hashPart2;
  }
  mapping (uint64 => userAttributes) allUsers;

  struct publicKey {
      bytes32 hashPart1;
      bytes32 hashPart2;
  }
  mapping (address =>  publicKey) publicKeys;

  struct IPFSCiphertext {
    address sender;
    address sdmSender;
    bytes32 hashPart1;
    bytes32 hashPart2;
  }
  mapping (uint64 => IPFSCiphertext) allLinks;

  function setUserAttributes(uint64 _instanceID, bytes32 _hash1, bytes32 _hash2) public {
    allUsers[_instanceID].hashPart1 = _hash1;
    allUsers[_instanceID].hashPart2 = _hash2;
  }

  function getUserAttributes(uint64 _instanceID) public view returns (bytes memory) {
    bytes32 p1 = allUsers[_instanceID].hashPart1;
    bytes32 p2 = allUsers[_instanceID].hashPart2;
    bytes memory joined = new bytes(64);
    assembly {
      mstore(add(joined, 32), p1)
      mstore(add(joined, 64), p2)
    }
    return joined;
  }

  function setPublicKeys(bytes32 _hash1, bytes32 _hash2) public {
    publicKeys[msg.sender].hashPart1 = _hash1;
    publicKeys[msg.sender].hashPart2 = _hash2;
  }

  function getPublicKeys(address _address) public view returns (bytes memory) {
    bytes32 p2 = publicKeys[_address].hashPart1;
    bytes32 p3 = publicKeys[_address].hashPart2;
    bytes memory joined = new bytes(64);
    assembly {
      mstore(add(joined, 32), p2)
      mstore(add(joined, 64), p3)
    }
      return (joined);
  }

  function setIPFSLink(uint64 _messageID, address _address, bytes32 _hash1, bytes32 _hash2) public {
    allLinks[_messageID].sdmSender = msg.sender;
    allLinks[_messageID].sender = _address;
    allLinks[_messageID].hashPart1 = _hash1;
    allLinks[_messageID].hashPart2 = _hash2;
  }

  function getIPFSLink(uint64 _messageID) public view returns (address, bytes memory) {
    address sender = allLinks[_messageID].sender;
    bytes32 p1 = allLinks[_messageID].hashPart1;
    bytes32 p2 = allLinks[_messageID].hashPart2;
    bytes memory joined = new bytes(64);
    assembly {
      mstore(add(joined, 32), p1)
      mstore(add(joined, 64), p2)
    }
    return (sender, joined);
  }

}
