// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title IRouter
 * @notice Shared interface and types for Router contract
 */
interface IRouter {
    struct SwapStep {
        address dex;
        address tokenIn;
        address tokenOut;
        address pool;
        uint256 amountIn;
        uint256 minAmountOut;
    }
    
    function executeArbitrage(
        SwapStep[] calldata steps,
        uint256 minProfit
    ) external returns (uint256);
}
