import hashlib
import json


def hash_block(block):
    """Return Hash Block"""  # Hash
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [tx.to_order() for tx in hashable_block['transactions']]
    return hashlib.sha256(json.dumps(hashable_block, sort_keys=True).encode()).hexdigest()


def hash_256(string):
    return hashlib.sha256(string).hexdigest()
