/**
 * BloXroute Manager
 * Manages private relay submission via BloXroute
 */

const axios = require('axios');

class BloXrouteManager {
    /**
     * Initialize BloXroute Manager
     * @param {string} authToken - BloXroute authentication token
     * @param {string} endpoint - BloXroute endpoint URL
     */
    constructor(authToken, endpoint = 'https://api.blxrbdn.com') {
        this.authToken = authToken;
        this.endpoint = endpoint;
        this.submittedTxs = [];
    }

    /**
     * Submit transaction to BloXroute private relay
     * @param {Object} tx - Signed transaction
     * @param {Object} options - Submission options
     * @returns {Promise<Object>} Submission result
     */
    async submitTransaction(tx, options = {}) {
        const {
            frontRunningProtection = true,
            mevProtection = true,
            fallbackToPublic = false
        } = options;

        try {
            const payload = {
                transaction: tx.rawTransaction || tx,
                blockchain_network: 'Polygon',
                mev_builders: {
                    'all': mevProtection
                },
                frontrunning_protection: frontRunningProtection,
                fallback_to_public_mempool: fallbackToPublic
            };

            const response = await axios.post(
                `${this.endpoint}/api/v1/relay/transaction`,
                payload,
                {
                    headers: {
                        'Authorization': this.authToken,
                        'Content-Type': 'application/json'
                    },
                    timeout: 5000
                }
            );

            const result = {
                success: true,
                txHash: response.data.tx_hash || 'unknown',
                timestamp: Date.now()
            };

            this.submittedTxs.push(result);

            return result;
        } catch (error) {
            return {
                success: false,
                error: error.message,
                timestamp: Date.now()
            };
        }
    }

    /**
     * Submit bundle of transactions
     * @param {Array<Object>} txs - Array of signed transactions
     * @param {Object} options - Bundle options
     * @returns {Promise<Object>} Bundle submission result
     */
    async submitBundle(txs, options = {}) {
        const {
            targetBlock = null,
            minTimestamp = null,
            maxTimestamp = null
        } = options;

        try {
            const payload = {
                txs: txs.map(tx => tx.rawTransaction || tx),
                blockchain_network: 'Polygon',
                block_number: targetBlock,
                min_timestamp: minTimestamp,
                max_timestamp: maxTimestamp
            };

            const response = await axios.post(
                `${this.endpoint}/api/v1/relay/bundle`,
                payload,
                {
                    headers: {
                        'Authorization': this.authToken,
                        'Content-Type': 'application/json'
                    },
                    timeout: 5000
                }
            );

            return {
                success: true,
                bundleHash: response.data.bundle_hash || 'unknown',
                timestamp: Date.now()
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                timestamp: Date.now()
            };
        }
    }

    /**
     * Get submission statistics
     * @returns {Object} Submission stats
     */
    getStats() {
        const successful = this.submittedTxs.filter(tx => tx.success).length;
        const failed = this.submittedTxs.length - successful;

        return {
            total: this.submittedTxs.length,
            successful,
            failed,
            successRate: this.submittedTxs.length > 0 
                ? (successful / this.submittedTxs.length * 100).toFixed(2) + '%'
                : '0%'
        };
    }

    /**
     * Clear submission history
     */
    clearHistory() {
        this.submittedTxs = [];
    }
}

module.exports = { BloXrouteManager };
