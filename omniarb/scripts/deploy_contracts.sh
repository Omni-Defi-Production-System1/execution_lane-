#!/bin/bash
# Deploy OmniArb contracts to Polygon

set -e

echo "=========================================="
echo "OmniArb Contract Deployment"
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

# Validate configuration
if [ -z "$PRIVATE_KEY" ]; then
    echo "Error: PRIVATE_KEY not set in .env"
    exit 1
fi

if [ "$POLYGON_CHAIN_ID" != "137" ]; then
    echo "Error: POLYGON_CHAIN_ID must be 137"
    exit 1
fi

echo "Deploying to Polygon (Chain ID: 137)"
echo "RPC: $POLYGON_RPC_URL"
echo ""

# Check for Foundry
if ! command -v forge &> /dev/null; then
    echo "Foundry not found. Checking for Hardhat..."
    
    if [ ! -f package.json ]; then
        echo "Setting up Hardhat..."
        npm init -y
        npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
    fi
    
    echo "Error: Please install Foundry (https://getfoundry.sh/) for contract deployment"
    echo "Or configure Hardhat deployment scripts"
    exit 1
fi

# Deploy with Foundry
cd contracts

echo "Deploying Router contract..."
ROUTER=$(forge create Router \
    --rpc-url "$POLYGON_RPC_URL" \
    --private-key "$PRIVATE_KEY" \
    --json | jq -r '.deployedTo')

echo "Router deployed at: $ROUTER"
echo ""

echo "Deploying HFT contract..."
HFT=$(forge create HFT \
    --rpc-url "$POLYGON_RPC_URL" \
    --private-key "$PRIVATE_KEY" \
    --constructor-args "$AAVE_POOL_ADDRESS" "$ROUTER" \
    --json | jq -r '.deployedTo')

echo "HFT deployed at: $HFT"
echo ""

cd ..

# Update .env file
echo "Updating .env with deployed addresses..."
if grep -q "ROUTER_ADDRESS=" .env; then
    sed -i "s|ROUTER_ADDRESS=.*|ROUTER_ADDRESS=$ROUTER|" .env
else
    echo "ROUTER_ADDRESS=$ROUTER" >> .env
fi

if grep -q "HFT_ADDRESS=" .env; then
    sed -i "s|HFT_ADDRESS=.*|HFT_ADDRESS=$HFT|" .env
else
    echo "HFT_ADDRESS=$HFT" >> .env
fi

echo ""
echo "=========================================="
echo "Deployment Complete"
echo "=========================================="
echo ""
echo "Router: $ROUTER"
echo "HFT: $HFT"
echo ""
echo "Addresses saved to .env"
echo ""
