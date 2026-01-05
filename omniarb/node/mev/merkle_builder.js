/**
 * Merkle Builder
 * Builds Merkle proofs for MEV protection
 */

const { ethers } = require('ethers');

class MerkleBuilder {
    constructor() {
        this.leaves = [];
    }

    /**
     * Add transaction to merkle tree
     * @param {Object} tx - Transaction object
     */
    addTransaction(tx) {
        const txHash = this._hashTransaction(tx);
        this.leaves.push(txHash);
    }

    /**
     * Build merkle root
     * @returns {string} Merkle root hash
     */
    buildRoot() {
        if (this.leaves.length === 0) {
            return ethers.ZeroHash;
        }

        let currentLevel = [...this.leaves];

        while (currentLevel.length > 1) {
            const nextLevel = [];

            for (let i = 0; i < currentLevel.length; i += 2) {
                if (i + 1 < currentLevel.length) {
                    const combined = ethers.concat([currentLevel[i], currentLevel[i + 1]]);
                    const hash = ethers.keccak256(combined);
                    nextLevel.push(hash);
                } else {
                    // Odd number of nodes, duplicate last one
                    nextLevel.push(currentLevel[i]);
                }
            }

            currentLevel = nextLevel;
        }

        return currentLevel[0];
    }

    /**
     * Get proof for transaction at index
     * @param {number} index - Transaction index
     * @returns {Array<string>} Merkle proof
     */
    getProof(index) {
        if (index >= this.leaves.length) {
            throw new Error('Index out of bounds');
        }

        const proof = [];
        let currentLevel = [...this.leaves];
        let currentIndex = index;

        while (currentLevel.length > 1) {
            const isRightNode = currentIndex % 2 === 1;
            const siblingIndex = isRightNode ? currentIndex - 1 : currentIndex + 1;

            if (siblingIndex < currentLevel.length) {
                proof.push(currentLevel[siblingIndex]);
            }

            currentIndex = Math.floor(currentIndex / 2);
            
            const nextLevel = [];
            for (let i = 0; i < currentLevel.length; i += 2) {
                if (i + 1 < currentLevel.length) {
                    const combined = ethers.concat([currentLevel[i], currentLevel[i + 1]]);
                    const hash = ethers.keccak256(combined);
                    nextLevel.push(hash);
                } else {
                    nextLevel.push(currentLevel[i]);
                }
            }
            
            currentLevel = nextLevel;
        }

        return proof;
    }

    /**
     * Hash transaction for merkle tree
     * @param {Object} tx - Transaction object
     * @returns {string} Transaction hash
     * @private
     */
    _hashTransaction(tx) {
        const encoded = ethers.AbiCoder.defaultAbiCoder().encode(
            ['address', 'bytes', 'uint256'],
            [tx.to || ethers.ZeroAddress, tx.data || '0x', tx.value || 0]
        );
        return ethers.keccak256(encoded);
    }

    /**
     * Clear merkle tree
     */
    clear() {
        this.leaves = [];
    }

    /**
     * Get number of transactions
     * @returns {number} Transaction count
     */
    getTransactionCount() {
        return this.leaves.length;
    }
}

module.exports = { MerkleBuilder };
