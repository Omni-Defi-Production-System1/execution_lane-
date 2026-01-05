// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./IRouter.sol";

/**
 * @title HFT (High-Frequency Trading)
 * @notice Flashloan receiver contract for atomic arbitrage execution
 * @dev Receives flashloans from Aave V3 and executes arbitrage
 */

interface IFlashLoanReceiver {
    function executeOperation(
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata premiums,
        address initiator,
        bytes calldata params
    ) external returns (bool);
}

interface IPool {
    function flashLoan(
        address receiverAddress,
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata modes,
        address onBehalfOf,
        bytes calldata params,
        uint16 referralCode
    ) external;
}

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract HFT is IFlashLoanReceiver {
    address public immutable owner;
    address public immutable aavePool;
    address public immutable router;
    
    // Core invariants
    uint256 public constant CHAIN_ID = 137; // Polygon only
    
    event FlashloanExecuted(
        address indexed asset,
        uint256 amount,
        uint256 premium,
        uint256 profit
    );
    
    event ArbitrageFailed(
        string reason
    );
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    modifier onlyAavePool() {
        require(msg.sender == aavePool, "Not Aave pool");
        _;
    }
    
    constructor(address _aavePool, address _router) {
        require(block.chainid == CHAIN_ID, "Wrong chain");
        owner = msg.sender;
        aavePool = _aavePool;
        router = _router;
    }
    
    /**
     * @notice Initiate flashloan arbitrage
     * @param asset Token to flashloan
     * @param amount Amount to borrow
     * @param params Encoded arbitrage parameters
     */
    function initiateArbitrage(
        address asset,
        uint256 amount,
        bytes calldata params
    ) external onlyOwner {
        require(asset != address(0), "Invalid asset");
        require(amount > 0, "Invalid amount");
        
        address[] memory assets = new address[](1);
        assets[0] = asset;
        
        uint256[] memory amounts = new uint256[](1);
        amounts[0] = amount;
        
        uint256[] memory modes = new uint256[](1);
        modes[0] = 0; // No debt - must repay in same transaction
        
        IPool(aavePool).flashLoan(
            address(this),
            assets,
            amounts,
            modes,
            address(this),
            params,
            0
        );
    }
    
    /**
     * @notice Flashloan callback - executes arbitrage
     * @dev Called by Aave Pool during flashloan
     */
    function executeOperation(
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata premiums,
        address initiator,
        bytes calldata params
    ) external override onlyAavePool returns (bool) {
        require(initiator == address(this), "Invalid initiator");
        require(assets.length == 1, "Only single asset supported");
        
        address asset = assets[0];
        uint256 amount = amounts[0];
        uint256 premium = premiums[0];
        uint256 amountOwed = amount + premium;
        
        // Decode arbitrage parameters
        (IRouter.SwapStep[] memory steps, uint256 minProfit) = abi.decode(
            params,
            (IRouter.SwapStep[], uint256)
        );
        
        // Transfer borrowed amount to router
        IERC20(asset).transfer(router, amount);
        
        // Execute arbitrage
        try IRouter(router).executeArbitrage(steps, minProfit) returns (uint256 profit) {
            // Get funds back from router
            uint256 balance = IERC20(asset).balanceOf(address(this));
            
            // Ensure we can repay flashloan
            require(balance >= amountOwed, "Insufficient funds to repay");
            
            // Approve Aave pool to take repayment
            IERC20(asset).approve(aavePool, amountOwed);
            
            emit FlashloanExecuted(asset, amount, premium, profit);
            
            return true;
        } catch Error(string memory reason) {
            emit ArbitrageFailed(reason);
            revert(reason);
        }
    }
    
    /**
     * @notice Withdraw tokens
     * @param token Token address
     * @param amount Amount to withdraw
     */
    function withdrawToken(address token, uint256 amount) external onlyOwner {
        IERC20(token).transfer(owner, amount);
    }
    
    /**
     * @notice Withdraw native currency
     */
    function withdrawNative() external onlyOwner {
        payable(owner).transfer(address(this).balance);
    }
    
    receive() external payable {}
}
