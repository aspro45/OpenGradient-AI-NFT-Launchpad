// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MinimalERC721 {
    string public name;
    string public symbol;
    uint256 public nextTokenId;
    
    mapping(uint256 => address) private _owners;
    mapping(address => uint256) private _balances;

    event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);

    constructor(string memory _name, string memory _symbol) {
        name = _name;
        symbol = _symbol;
    }

    function mint(address to) public {
        require(to != address(0), "Cannot mint to zero address");
        
        uint256 tokenId = nextTokenId;
        nextTokenId++;

        _balances[to] += 1;
        _owners[tokenId] = to;

        emit Transfer(address(0), to, tokenId);
    }

    function ownerOf(uint256 tokenId) public view returns (address) {
        address owner = _owners[tokenId];
        require(owner != address(0), "Token does not exist");
        return owner;
    }

    function balanceOf(address owner) public view returns (uint256) {
        require(owner != address(0), "Query for zero address");
        return _balances[owner];
    }
}
