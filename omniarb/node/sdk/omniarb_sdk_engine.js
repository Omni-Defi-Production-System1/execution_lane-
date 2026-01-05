/**
 * OmniArb SDK Engine
 * Node.js SDK for eth_call simulation and gas estimation
 */

const { ethers } = require('ethers');

class OmniArbSDKEngine {
    /**
     * Initialize SDK Engine
     * @param {string} rpcUrl - Polygon RPC URL
     * @param {number} chainId - Chain ID (must be 137 for Polygon)
     */
    constructor(rpcUrl, chainId = 137) {
        if (chainId !== 137) {
            throw new Error(`Invalid chain ID: ${chainId}. Only Polygon (137) is supported.`);
        }
        
        this.rpcUrl = rpcUrl;
        this.chainId = chainId;
        this.provider = new ethers.JsonRpcProvider(rpcUrl);
    }

    /**
     * Simulate transaction with eth_call
     * @param {Object} tx - Transaction object
     * @returns {Promise<Object>} Simulation result
     */
    async simulateCall(tx) {
        try {
            const result = await this.provider.call({
                to: tx.to,
                data: tx.data,
                value: tx.value || 0,
                from: tx.from || ethers.ZeroAddress
            });
            
            return {
                success: true,
                returnData: result
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                reason: error.reason || 'Unknown'
            };
        }
    }

    /**
     * Estimate gas for transaction
     * @param {Object} tx - Transaction object
     * @returns {Promise<Object>} Gas estimation result
     */
    async estimateGas(tx) {
        try {
            const gasLimit = await this.provider.estimateGas({
                to: tx.to,
                data: tx.data,
                value: tx.value || 0,
                from: tx.from || ethers.ZeroAddress
            });
            
            return {
                success: true,
                gasLimit: gasLimit.toString(),
                gasLimitNumber: Number(gasLimit)
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                reason: error.reason || 'Unknown'
            };
        }
    }

    /**
     * Get current gas price
     * @returns {Promise<Object>} Gas price info
     */
    async getGasPrice() {
        try {
            const feeData = await this.provider.getFeeData();
            
            return {
                success: true,
                gasPrice: feeData.gasPrice ? feeData.gasPrice.toString() : '0',
                maxFeePerGas: feeData.maxFeePerGas ? feeData.maxFeePerGas.toString() : '0',
                maxPriorityFeePerGas: feeData.maxPriorityFeePerGas ? feeData.maxPriorityFeePerGas.toString() : '0'
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Run preflight checks on transaction
     * @param {Object} tx - Transaction object
     * @returns {Promise<Object>} Preflight result
     */
    async runPreflight(tx) {
        const results = {
            success: false,
            checks: {},
            errors: []
        };

        // Simulation check
        const simResult = await this.simulateCall(tx);
        results.checks.simulation = simResult;

        if (!simResult.success) {
            results.errors.push(`Simulation failed: ${simResult.error}`);
            return results;
        }

        // Gas estimation check
        const gasResult = await this.estimateGas(tx);
        results.checks.gasEstimation = gasResult;

        if (!gasResult.success) {
            results.errors.push(`Gas estimation failed: ${gasResult.error}`);
            return results;
        }

        // All checks passed
        results.success = true;
        results.estimatedGas = gasResult.gasLimitNumber;

        return results;
    }

    /**
     * Get current block number
     * @returns {Promise<number>} Block number
     */
    async getBlockNumber() {
        return await this.provider.getBlockNumber();
    }

    /**
     * Get transaction count for address (nonce)
     * @param {string} address - Address to check
     * @returns {Promise<number>} Transaction count
     */
    async getTransactionCount(address) {
        return await this.provider.getTransactionCount(address);
    }
}

module.exports = { OmniArbSDKEngine };
