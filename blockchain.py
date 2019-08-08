import json
import pickle
from collections import OrderedDict
from functools import reduce

from hash_util import hash_block, hash_256

MINING_REWARD = 10
genesis_block = {'previous_hash': '',
                 'index': 0,
                 'transactions': [],
                 'proof': 100}

blockchain = [genesis_block]
open_transaction = []
owner = 'AgentFx'
perticipants = {'AgentFx'}


# Initialize BlockChain
def load_file():
    with open('blockchain.txt', mode='r') as f:
        filecontent = f.readlines()
        global blockchain
        global open_transaction
        blockchain = json.loads(filecontent[0][:-1])
        updated_blockchain = []
        for block in blockchain:
            updated_block = {
                'previous_hash': block['previous_hash'],
                'index': block['index'],
                'proof': block['proof'],
                'transactions': [OrderedDict(
                    [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in
                    block['transactions']]
            }
            updated_blockchain.append(updated_block)
        blockchain = updated_blockchain
        open_transaction = json.loads(filecontent[1])
        updated_transactions = []
        for tx in open_transaction:
            updated_transaction = OrderedDict(
                [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])])
            updated_transactions.append(updated_transaction)
        open_transaction = updated_transactions


def load_file_pickle():
    with open('blockchain.p', mode='rb') as f:
        file_content = pickle.loads(f.read())
        global blockchain
        global open_transaction
        blockchain = file_content['chain']
        open_transaction = file_content['ot']


load_file_pickle()


# load_file()


def save_file():
    with open('blockchain.p', mode='wb') as f:
        # f.write(json.dumps(blockchain))
        # f.write('\n')
        # f.write(json.dumps(open_transaction))
        save_data = {
            'chain': blockchain,
            'ot': open_transaction
        }
        f.write(pickle.dumps(save_data))


def get_last_blockchain_value():
    """Returns The Last Value Of Current Blockchain"""  # Last Block
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def valid_proof(transactions, last_hash, proof):
    """Validating proof"""  # validating proof
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_256(guess)
    return guess_hash[0:2] == '00'


def proof_of_work():
    """Generating proof of work"""  # Proof of work
    last_block = get_last_blockchain_value()
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transaction, last_hash, proof):
        proof += 1
    return proof


def get_balance(peticipant):
    """Return Balance"""  # Balance
    tx_sender = [[tx['amount'] for tx in block['transactions']
                  if tx['sender'] == peticipant]
                 for block in blockchain]
    open_tx_sender = [tx['amount'] for tx in open_transaction
                      if tx['sender'] == peticipant]
    tx_sender.append(open_tx_sender)
    balance_send = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0,
                          tx_sender, 0)

    tx_receipent = [[tx['amount'] for tx in block['transactions']
                     if tx['recipient'] == peticipant]
                    for block in blockchain]

    balance_rec = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0,
                         tx_receipent, 0)
    return balance_rec - balance_send


def add_transaction(receipent, sender=owner, amount=1.0):
    """Add a Transaction"""  # Add Transaction
    transaction = {'sender': sender,
                   'recipient': receipent,
                   'amount': amount
                   }
    transaction = OrderedDict([('sender', sender), ('recipient', receipent), ('amount', amount)])
    if verify_transaction(transaction):
        open_transaction.append(transaction)
        save_file()
        perticipants.add(sender)
        perticipants.add(receipent)
        return True
    return False


def mine_block():
    """Mining Blocks"""  # Mining
    last_block = get_last_blockchain_value()
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    reward_transaction = {'sender': 'MINING',
                          'recipient': owner,
                          'amount': MINING_REWARD
                          }
    reward_transaction = OrderedDict([('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
    copy_transaction = open_transaction[:]
    copy_transaction.append(reward_transaction)
    block = {'previous_hash': hashed_block,
             'index': len(blockchain),
             'transactions': copy_transaction,
             'proof': proof
             }
    blockchain.append(block)
    return True


def get_transaction_value():
    """Transaction input"""  # Transaction input
    # tx_sender = input("Sender:")
    tx_receipent = input("Recipient: ")
    tx_amount = float(input("Amount: "))
    return tx_receipent, tx_amount


def get_user_choice():
    """User Chjoice"""  # User Choice
    return input("Your Choice ")


def print_blockchain():
    """Print Blockchain"""  # Print BlockChain
    for block in blockchain:
        print("Outputting Block")
        print(block)
    else:
        print("-" * 20)


def verify_chain():
    """Verify Chain"""  # Verify chain
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            print('proof of work in invalid')
            return False
    return True


def verify_transaction(transaction):
    """Verify transaction"""  # Verify Transaction
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transaction])


# tx_amount = get_transaction_value()
# add_value(tx_amount)

waiting_for_input = True
# Driver
while waiting_for_input:
    print("Enter Choice")
    print("1:Add transaction")
    print("2:Mine bLock")
    print("3:Perticipents: ")
    print("4: Check Transaction valididty: ")
    print("h: Manipulate Transaction")
    print("q:Quit")
    user_choice = get_user_choice()
    if user_choice == '1':
        tx_data = get_transaction_value()
        receipent, amount = tx_data
        if add_transaction(receipent, amount=amount):
            print("Successful")
        else:
            print("Failed")
        # print(open_transaction)
    elif user_choice == '2':
        if mine_block():
            open_transaction = []
            save_file()
    elif user_choice == '3':
        print(perticipants)
    elif user_choice == '4':
        if verify_transactions():
            print("Valid Transaction")
        else:
            print("Invalid transaction")
    elif user_choice == 'q':
        waiting_for_input = False
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = {'previous_hash': '',
                             'index': 0,
                             'transactions': [{'sender': 'fxpro',
                                               'recipient': 'fxp',
                                               'amount': '500'
                                               }]}
    else:
        print("Invalid Choice")
    if not verify_chain():
        print("Invalid Blockchain")
        break
    print('Balance of  {} : {:6.2f}'.format('AgentFx', get_balance('AgentFx')))
else:
    print("User Left")
