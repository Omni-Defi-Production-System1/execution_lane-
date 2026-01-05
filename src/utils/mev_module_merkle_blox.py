# mev_module.py

import time
import hashlib
import hmac
from typing import List, Tuple
from eth_utils import keccak, to_bytes, to_hex


### -----------------------------
### MERKLE MEV TREE COMPONENTS
### -----------------------------

def hash_leaf(data: str) -> bytes:
    return keccak(text=data)

def build_merkle_tree(leaves: List[str]) -> Tuple[str, List[bytes]]:
    """Builds a Merkle Tree from a list of leaf strings and returns the root."""
    hashed_leaves = [hash_leaf(leaf) for leaf in leaves]
    tree = hashed_leaves.copy()
    while len(tree) > 1:
        temp = []
        for i in range(0, len(tree), 2):
            left = tree[i]
            right = tree[i+1] if i+1 < len(tree) else tree[i]
            combined = keccak(left + right)
            temp.append(combined)
        tree = temp
    root = to_hex(tree[0])
    return root, hashed_leaves

def generate_merkle_proof(index: int, hashed_leaves: List[bytes]) -> List[bytes]:
    """Generate a Merkle proof for a leaf at a given index."""
    proof = []
    layer = hashed_leaves
    while len(layer) > 1:
        next_layer = []
        for i in range(0, len(layer), 2):
            left = layer[i]
            right = layer[i+1] if i+1 < len(layer) else layer[i]
            combined = keccak(left + right)
            next_layer.append(combined)
            if i == index or i+1 == index:
                sibling = right if i == index else left
                proof.append(sibling)
        index = index // 2
        layer = next_layer
    return proof


def verify_merkle_proof(leaf: str, proof: List[bytes], root: str) -> bool:
    """Verify a Merkle proof from a leaf."""
    computed = hash_leaf(leaf)
    for sibling in proof:
        if computed < sibling:
            computed = keccak(computed + sibling)
        else:
            computed = keccak(sibling + computed)
    return to_hex(computed) == root


### -----------------------------
### MYBLOX ROUTE HEADER SYSTEM
### -----------------------------

class MyBloxHeader:
    def __init__(self, route_id: str, route_path: str, bot_id: str, secret_key: str):
        self.route_id = route_id
        self.route_path = route_path
        self.timestamp = int(time.time())
        self.bot_id = bot_id
        self.secret_key = secret_key.encode()

    def route_hash(self) -> str:
        return hashlib.sha256(self.route_path.encode()).hexdigest()

    def header_dict(self) -> dict:
        return {
            "route_id": self.route_id,
            "timestamp": self.timestamp,
            "bot_id": self.bot_id,
            "route_hash": self.route_hash(),
        }

    def generate_blox_key(self) -> str:
        message = f"{self.timestamp}{self.route_path}".encode()
        return hmac.new(self.secret_key, message, hashlib.sha256).hexdigest()

    def inject_into_calldata(self, calldata: str) -> str:
        # Append header data to calldata for verification
        key = self.generate_blox_key()
        header = self.header_dict()
        header_encoded = f"{header['route_id']}|{header['timestamp']}|{header['bot_id']}|{header['route_hash']}|{key}"
        encoded = header_encoded.encode().hex()
        return calldata + encoded


### -----------------------------
### SAMPLE USAGE
### -----------------------------

if __name__ == "__main__":
    # Step 1: Generate Merkle tree
    candidate_routes = ["USDC>WETH>WBTC", "USDT>DAI>USDC", "WETH>WMATIC>USDC"]
    root, leaves = build_merkle_tree(candidate_routes)
    print("Merkle Root:", root)

    # Step 2: Get proof for route 0
    proof = generate_merkle_proof(0, leaves)
    verified = verify_merkle_proof(candidate_routes[0], proof, root)
    print("Proof Verified:", verified)

    # Step 3: Create MyBlox header
    header = MyBloxHeader(route_id="0xabc123", route_path=candidate_routes[0], bot_id="dual-apex-01", secret_key="super_secret")
    key = header.generate_blox_key()
    print("Blox Key:", key)

    # Step 4: Inject header into calldata
    dummy_calldata = "0xdeadbeef"
    final_data = header.inject_into_calldata(dummy_calldata)
    print("Final Calldata:", final_data)
