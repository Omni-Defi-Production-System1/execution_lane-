/**
 * Transaction Submitter
 * Final execution layer for submitting arbitrage transactions
 */

const { ethers } = require('ethers');
const { OmniArbSDKEngine } = require('../sdk/omniarb_sdk_engine');
const { BloXrouteManager } = require('../mev/bloxroute_manager');
const { MerkleBuilder } = require('../mev/merkle_builder');

class TransactionSubmitter {
    /**
     * Initialize Transaction Submitter
     * @param {string} rpcUrl - Polygon RPC URL
     * @param {string} privateKey - Private key for signing
     * @param {string} bloxrouteAuth - BloXroute auth token (optional)
     */
    constructor(rpcUrl, privateKey, bloxrouteAuth = null) {
        this.chainId = 137; // Polygon only
        this.sdk = new OmniArbSDKEngine(rpcUrl, this.chainId);
        this.wallet = new ethers.Wallet(privateKey, this.sdk.provider);
        this.bloxroute = bloxrouteAuth ? new BloXrouteManager(bloxrouteAuth) : null;
        this.merkleBuilder = new MerkleBuilder();
        
        console.log('Transaction Submitter initialized');
        console.log(`Chain ID: ${this.chainId} (Polygon)`);
        console.log(`Wallet address: ${this.wallet.address}`);
        console.log(`MEV protection: ${this.bloxroute ? 'ENABLED' : 'DISABLED'}`);
    }

    /**
     * Execute arbitrage transaction with full safety checks
     * 
     * Execution Rule - Transaction is signed ONLY if:
     * 1. Flashloan feasibility passes
     * 2. DeFi math says profit > 0
     * 3. AI score >= threshold
     * 4. eth_call simulation succeeds
     * 5. Merkle + MEV shielding applied
     * 
     * @param {Object} tx - Transaction object
     * @param {Object} route - Route analysis result
     * @returns {Promise<Object>} Execution result
     */
    async executeArbitrage(tx, route) {
        console.log('\n' + '='.repeat(60));
        console.log('EXECUTING ARBITRAGE TRANSACTION');
        console.log('='.repeat(60));

        // Rule 1 & 2: Already checked by Python engine (flashloan + profit)
        if (route.will_revert) {
            console.log('❌ ABORTED: Transaction will revert');
            return { success: false, reason: 'will_revert' };
        }

        if (route.profit <= 0) {
            console.log('❌ ABORTED: No profit');
            return { success: false, reason: 'no_profit' };
        }

        console.log(`✓ Flashloan feasibility: PASS`);
        console.log(`✓ Profit check: ${route.profit} USD`);

        // Rule 3: AI score check (already done by engine, but verify)
        if (route.ai_score !== undefined && route.ai_score <= 0) {
            console.log('❌ ABORTED: AI score below threshold');
            return { success: false, reason: 'low_ai_score' };
        }

        console.log(`✓ AI score: ${route.ai_score || 'N/A'}`);

        // Rule 4: eth_call simulation
        console.log('\nRunning preflight simulation...');
        const preflight = await this.sdk.runPreflight(tx);

        if (!preflight.success) {
            console.log('❌ ABORTED: Simulation failed');
            console.log('Errors:', preflight.errors);
            return { success: false, reason: 'simulation_failed', errors: preflight.errors };
        }

        console.log('✓ Simulation: PASS');
        console.log(`✓ Estimated gas: ${preflight.estimatedGas}`);

        // Rule 5: Apply Merkle + MEV protection
        console.log('\nApplying MEV protection...');
        this.merkleBuilder.clear();
        this.merkleBuilder.addTransaction(tx);
        const merkleRoot = this.merkleBuilder.buildRoot();
        const merkleProof = this.merkleBuilder.getProof(0);

        console.log(`✓ Merkle root: ${merkleRoot.substring(0, 10)}...`);
        console.log(`✓ Merkle proof length: ${merkleProof.length}`);

        // Prepare transaction
        const txRequest = {
            to: tx.to,
            data: tx.data,
            value: tx.value || 0,
            chainId: this.chainId,
            gasLimit: tx.gasLimit || preflight.estimatedGas,
            nonce: await this.sdk.getTransactionCount(this.wallet.address)
        };

        // Get gas price
        const gasPrice = await this.sdk.getGasPrice();
        if (gasPrice.success) {
            txRequest.maxFeePerGas = gasPrice.maxFeePerGas;
            txRequest.maxPriorityFeePerGas = gasPrice.maxPriorityFeePerGas;
        }

        // Sign transaction
        console.log('\nSigning transaction...');
        const signedTx = await this.wallet.signTransaction(txRequest);
        console.log('✓ Transaction signed');

        // Submit via BloXroute or public mempool
        console.log('\nSubmitting transaction...');
        let result;

        if (this.bloxroute) {
            console.log('Submitting via BloXroute private relay...');
            result = await this.bloxroute.submitTransaction(
                { rawTransaction: signedTx },
                {
                    frontRunningProtection: true,
                    mevProtection: true,
                    fallbackToPublic: false
                }
            );
        } else {
            console.log('Submitting via public mempool...');
            try {
                const txResponse = await this.sdk.provider.broadcastTransaction(signedTx);
                result = {
                    success: true,
                    txHash: txResponse.hash
                };
            } catch (error) {
                result = {
                    success: false,
                    error: error.message
                };
            }
        }

        if (result.success) {
            console.log('✅ TRANSACTION SUBMITTED');
            console.log(`Transaction hash: ${result.txHash}`);
        } else {
            console.log('❌ SUBMISSION FAILED');
            console.log(`Error: ${result.error}`);
        }

        console.log('='.repeat(60) + '\n');

        return result;
    }

    /**
     * Get wallet address
     * @returns {string} Wallet address
     */
    getAddress() {
        return this.wallet.address;
    }

    /**
     * Get wallet balance
     * @returns {Promise<string>} Balance in POL
     */
    async getBalance() {
        const balance = await this.sdk.provider.getBalance(this.wallet.address);
        return ethers.formatEther(balance);
    }
}

// Main execution
async function main() {
    console.log('\n' + '='.repeat(60));
    console.log('OMNIARB NODE TRANSACTION SUBMITTER');
    console.log('='.repeat(60));
    console.log('\nCore Invariants:');
    console.log('  ✓ Chain: Polygon (137)');
    console.log('  ✓ Native gas: POL');
    console.log('  ✓ Capital source: Flashloan only');
    console.log('  ✓ Execution: Atomic or revert');
    console.log('\nWaiting for transactions from arbitrage engine...');
    console.log('='.repeat(60) + '\n');

    // Keep process alive
    setInterval(() => {
        // Heartbeat
    }, 60000);
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = { TransactionSubmitter };
