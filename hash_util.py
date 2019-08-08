import hashlib
import json
def hash_block(block):
    """Return Hash Block"""  # Hash
    return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

def hash_256(string):
    return hashlib.sha256(string).hexdigest()