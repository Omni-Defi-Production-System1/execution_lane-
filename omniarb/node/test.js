/**
 * OmniArb Node.js Test Suite
 */

const { OmniArbSDKEngine } = require('./sdk/omniarb_sdk_engine.js');
const { MerkleBuilder } = require('./mev/merkle_builder.js');
const { BloXrouteManager } = require('./mev/bloxroute_manager.js');

console.log('='.repeat(60));
console.log('OmniArb Node.js Test Suite');
console.log('='.repeat(60));
console.log();

let passed = 0;
let failed = 0;

function test(name, fn) {
    try {
        fn();
        console.log(`✓ ${name}`);
        passed++;
    } catch (error) {
        console.log(`✗ ${name}: ${error.message}`);
        failed++;
    }
}

// Test 1: SDK Engine initialization
test('SDK Engine initialization', () => {
    const sdk = new OmniArbSDKEngine('https://polygon-rpc.com', 137);
    if (sdk.chainId !== 137) throw new Error('Chain ID not set correctly');
    if (!sdk.provider) throw new Error('Provider not initialized');
});

// Test 2: SDK Engine rejects invalid chain
test('SDK Engine rejects invalid chain', () => {
    try {
        new OmniArbSDKEngine('https://ethereum-rpc.com', 1);
        throw new Error('Should have thrown error for invalid chain');
    } catch (error) {
        if (!error.message.includes('137')) {
            throw new Error('Wrong error message');
        }
    }
});

// Test 3: Merkle Builder initialization
test('Merkle Builder initialization', () => {
    const builder = new MerkleBuilder();
    if (!Array.isArray(builder.leaves)) throw new Error('Leaves not initialized');
    if (builder.leaves.length !== 0) throw new Error('Leaves should be empty');
});

// Test 4: Merkle Builder add transaction
test('Merkle Builder add transaction', () => {
    const builder = new MerkleBuilder();
    const tx = {
        to: '0x1234567890123456789012345678901234567890',
        data: '0x',
        value: 0
    };
    
    builder.addTransaction(tx);
    if (builder.getTransactionCount() !== 1) {
        throw new Error('Transaction not added');
    }
});

// Test 5: Merkle Builder build root
test('Merkle Builder build root', () => {
    const builder = new MerkleBuilder();
    const tx = {
        to: '0x1234567890123456789012345678901234567890',
        data: '0x',
        value: 0
    };
    
    builder.addTransaction(tx);
    const root = builder.buildRoot();
    
    if (!root || typeof root !== 'string') {
        throw new Error('Invalid root');
    }
    
    if (!root.startsWith('0x')) {
        throw new Error('Root should be hex string');
    }
});

// Test 6: Merkle Builder get proof
test('Merkle Builder get proof', () => {
    const builder = new MerkleBuilder();
    
    builder.addTransaction({ to: '0x1234567890123456789012345678901234567890', data: '0x', value: 0 });
    builder.addTransaction({ to: '0x2234567890123456789012345678901234567890', data: '0x', value: 0 });
    
    const proof = builder.getProof(0);
    
    if (!Array.isArray(proof)) {
        throw new Error('Proof should be array');
    }
});

// Test 7: BloXroute Manager initialization
test('BloXroute Manager initialization', () => {
    const manager = new BloXrouteManager('test-token', 'https://test-endpoint.com');
    
    if (manager.authToken !== 'test-token') {
        throw new Error('Auth token not set');
    }
    
    if (manager.endpoint !== 'https://test-endpoint.com') {
        throw new Error('Endpoint not set');
    }
    
    if (!Array.isArray(manager.submittedTxs)) {
        throw new Error('Submitted txs not initialized');
    }
});

// Test 8: BloXroute Manager stats
test('BloXroute Manager stats', () => {
    const manager = new BloXrouteManager('test-token');
    const stats = manager.getStats();
    
    if (typeof stats.total !== 'number') throw new Error('Invalid stats.total');
    if (typeof stats.successful !== 'number') throw new Error('Invalid stats.successful');
    if (typeof stats.failed !== 'number') throw new Error('Invalid stats.failed');
    if (typeof stats.successRate !== 'string') throw new Error('Invalid stats.successRate');
});

// Test 9: Module exports
test('All modules export correctly', () => {
    if (typeof OmniArbSDKEngine !== 'function') {
        throw new Error('OmniArbSDKEngine not exported');
    }
    if (typeof MerkleBuilder !== 'function') {
        throw new Error('MerkleBuilder not exported');
    }
    if (typeof BloXrouteManager !== 'function') {
        throw new Error('BloXrouteManager not exported');
    }
});

// Summary
console.log();
console.log('='.repeat(60));
console.log(`Test Results: ${passed} passed, ${failed} failed`);
console.log('='.repeat(60));
console.log();

process.exit(failed > 0 ? 1 : 0);
