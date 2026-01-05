#!/bin/bash
# Boot Lane01 - Start the OmniArb arbitrage system

set -e

echo "=========================================="
echo "OmniArb Lane-01 Boot Sequence"
echo "=========================================="
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "Error: .env file not found"
    echo "Please copy .env.example to .env and configure"
    exit 1
fi

# Source environment
source .env

# Validate chain ID
if [ "$POLYGON_CHAIN_ID" != "137" ]; then
    echo "Error: Invalid POLYGON_CHAIN_ID. Must be 137 for Polygon"
    exit 1
fi

echo "Chain ID: $POLYGON_CHAIN_ID ✓"
echo "RPC: $POLYGON_RPC_URL ✓"
echo ""

# Check contract addresses
if [ -z "$ROUTER_ADDRESS" ] || [ -z "$HFT_ADDRESS" ]; then
    echo "Warning: Contract addresses not set"
    echo "Run deploy_contracts.sh first to deploy contracts"
    echo ""
fi

echo "Core Invariants:"
echo "  - Chain: Polygon (137)"
echo "  - Native gas: POL (never ERC-20)"
echo "  - Tradable native: WMATIC"
echo "  - Capital source: Flashloan only"
echo "  - Execution: Atomic or revert"
echo "  - No prefunding allowed"
echo ""

# Start services
echo "Starting services..."
echo ""

if command -v docker-compose &> /dev/null; then
    echo "Using docker-compose..."
    docker-compose up -d
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    echo "Using docker compose..."
    docker compose up -d
else
    echo "Docker not available. Starting services manually..."
    
    # Start Python engine in background
    echo "Starting Python arbitrage engine..."
    cd python
    python -m engine.ultimate_arbitrage_engine &
    PYTHON_PID=$!
    cd ..
    
    # Start Node submitter in background
    echo "Starting Node transaction submitter..."
    cd node
    node tx/submitter.js &
    NODE_PID=$!
    cd ..
    
    echo ""
    echo "Services started:"
    echo "  - Python engine (PID: $PYTHON_PID)"
    echo "  - Node submitter (PID: $NODE_PID)"
    echo ""
    echo "To stop: kill $PYTHON_PID $NODE_PID"
fi

echo ""
echo "=========================================="
echo "Lane-01 Boot Complete"
echo "=========================================="
echo ""
echo "System is now monitoring for arbitrage opportunities"
echo "Logs: docker-compose logs -f (or check process output)"
echo ""
