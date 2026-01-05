// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title Router
 * @notice Atomic arbitrage router for flashloan-based execution
 * @dev Executes multi-hop swaps atomically or reverts
 */
interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

interface IDEXRouter {
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);
}

contract Router {
    address public immutable owner;
    
    struct SwapStep {
        address dex;
        address tokenIn;
        address tokenOut;
        address pool;
        uint256 amountIn;
        uint256 minAmountOut;
    }
    
    event ArbitrageExecuted(
        address indexed executor,
        uint256 profit,
        uint256 gasUsed
    );
    
    event SwapExecuted(
        address indexed dex,
        address indexed tokenIn,
        address indexed tokenOut,
        uint256 amountIn,
        uint256 amountOut
    );
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    constructor() {
        owner = msg.sender;
    }
    
    /**
     * @notice Execute multi-step arbitrage
     * @param steps Array of swap steps to execute
     * @param minProfit Minimum profit required (in final token)
     * @return finalProfit Final profit amount
     */
    function executeArbitrage(
        SwapStep[] calldata steps,
        uint256 minProfit
    ) external onlyOwner returns (uint256 finalProfit) {
        require(steps.length > 0, "No steps");
        
        uint256 gasStart = gasleft();
        uint256 initialBalance = IERC20(steps[0].tokenIn).balanceOf(address(this));
        
        // Execute each swap step
        for (uint256 i = 0; i < steps.length; i++) {
            _executeSwap(steps[i]);
        }
        
        // Calculate profit
        uint256 finalBalance = IERC20(steps[0].tokenIn).balanceOf(address(this));
        require(finalBalance > initialBalance, "No profit");
        
        finalProfit = finalBalance - initialBalance;
        require(finalProfit >= minProfit, "Profit below minimum");
        
        uint256 gasUsed = gasStart - gasleft();
        emit ArbitrageExecuted(msg.sender, finalProfit, gasUsed);
        
        return finalProfit;
    }
    
    /**
     * @notice Execute single swap step
     * @param step Swap step parameters
     */
    function _executeSwap(SwapStep calldata step) internal {
        require(step.dex != address(0), "Invalid DEX");
        require(step.tokenIn != address(0), "Invalid tokenIn");
        require(step.tokenOut != address(0), "Invalid tokenOut");
        require(step.amountIn > 0, "Invalid amount");
        
        // Approve DEX to spend tokens
        IERC20(step.tokenIn).approve(step.dex, step.amountIn);
        
        // Build path for swap
        address[] memory path = new address[](2);
        path[0] = step.tokenIn;
        path[1] = step.tokenOut;
        
        // Execute swap
        uint256 balanceBefore = IERC20(step.tokenOut).balanceOf(address(this));
        
        IDEXRouter(step.dex).swapExactTokensForTokens(
            step.amountIn,
            step.minAmountOut,
            path,
            address(this),
            block.timestamp + 60
        );
        
        uint256 balanceAfter = IERC20(step.tokenOut).balanceOf(address(this));
        uint256 amountOut = balanceAfter - balanceBefore;
        
        require(amountOut >= step.minAmountOut, "Insufficient output");
        
        emit SwapExecuted(step.dex, step.tokenIn, step.tokenOut, step.amountIn, amountOut);
    }
    
    /**
     * @notice Withdraw tokens from contract
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
