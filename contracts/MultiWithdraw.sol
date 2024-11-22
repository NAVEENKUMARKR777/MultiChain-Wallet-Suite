// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MultiWithdraw {
    address public owner;
    
    event MultipleWithdrawals(address[] recipients, uint256[] amounts);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    constructor() {
        owner = msg.sender;
    }
    
    function withdraw(address[] memory recipients, uint256[] memory amounts) public payable {
        require(recipients.length == amounts.length, "Recipients and amounts length mismatch");
        require(recipients.length > 0, "Empty recipients array");
        
        uint256 totalAmount = 0;
        for (uint256 i = 0; i < amounts.length; i++) {
            totalAmount += amounts[i];
        }
        
        require(msg.value >= totalAmount, "Insufficient funds sent");
        
        for (uint256 i = 0; i < recipients.length; i++) {
            require(recipients[i] != address(0), "Invalid recipient address");
            payable(recipients[i]).transfer(amounts[i]);
        }
        
        // Refund excess ETH if any
        uint256 excess = msg.value - totalAmount;
        if (excess > 0) {
            payable(msg.sender).transfer(excess);
        }
        
        emit MultipleWithdrawals(recipients, amounts);
    }
    
    function transferOwnership(address newOwner) public onlyOwner {
        require(newOwner != address(0), "New owner is the zero address");
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
    }
    
    // Allow contract to receive ETH
    receive() external payable {}
}
