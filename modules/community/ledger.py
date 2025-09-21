import hashlib, json, time
from web3 import Web3

# Connect to Ethereum testnet (Sepolia via Infura or Alchemy)
# Replace with your Infura/Alchemy endpoint and private key
INFURA_URL = "https://eth-sepolia.g.alchemy.com/v2/P7-7ClFr4tQg_Zca3Lnhq"
PRIVATE_KEY = "771b2e208374b2fdf3930e4057f97af569f537077ed171bab64fa27d6bdc46bb"

w3 = Web3(Web3.HTTPProvider(INFURA_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

def generate_hash(payload: dict) -> str:
    """
    Generate SHA256 hash for a payload.
    """
    raw = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def anchor_to_blockchain(ledger_hash: str) -> str:
    """
    Anchors a ledger hash to Ethereum Sepolia.
    Returns blockchain transaction hash.
    """
    try:
        tx = {
            "from": account.address,
            "to": account.address,   # self-send for anchoring
            "value": 0,
            "gas": 21000,
            "gasPrice": w3.to_wei("10", "gwei"),
            "nonce": w3.eth.get_transaction_count(account.address),
            "data": ledger_hash.encode("utf-8"),
        }
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        return tx_hash.hex()
    except Exception as e:
        return f"Blockchain anchoring failed: {str(e)}"
