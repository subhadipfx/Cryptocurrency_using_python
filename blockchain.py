import pickle
from functools import reduce

from utility.hash_util import hash_block
from block import Block
from transaction import Transaction
from utility.verification import Verification
from wallet import Wallet
import requests

MINING_REWARD = 10


class Blockchain:
    def __init__(self, node_id, port):
        genesis_block = Block(0, ' ', [], 100, 0)
        self.__chain = [genesis_block]
        self.__open_transactions = []
        self.node_id = node_id
        self.port = port
        self.__peer_nodes = set()
        self.load_file_pickle()

    def get_chain(self):
        return self.__chain[:]

    def get_open_transaction(self):
        return self.__open_transactions[:]

    def load_file_pickle(self):
        try:
            with open('blockchain-{}.p'.format(self.port), mode='rb') as f:
                file_content = pickle.loads(f.read())
                self.__chain = file_content['chain']
                self.__open_transactions = file_content['ot']
                self.__peer_nodes = set(file_content['nodes'])
        except (FileNotFoundError, IndexError):
            print('File Not Found')
        except ValueError:
            print('Value Error')
        finally:
            print('Cleanup')

    def save_file(self):
        try:
            with open('blockchain-{}.p'.format(self.port), mode='wb') as f:
                # f.write(json.dumps(blockchain))
                # f.write('\n')
                # f.write(json.dumps(open_transaction))
                save_data = {
                    'chain': self.__chain,
                    'ot': self.__open_transactions,
                    'nodes': self.__peer_nodes
                }
                f.write(pickle.dumps(save_data))
        except IOError:
            print('Saveing failed')

    def get_last_blockchain_value(self):
        """Returns The Last Value Of Current Blockchain"""  # Last Block
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    def proof_of_work(self):
        """Generating proof of work"""  # Proof of work
        last_block = self.get_last_blockchain_value()
        last_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self, sender=None):
        """Return Balance"""  # Balance
        if sender is None:
            if self.node_id is None:
                return None
            perticipant = self.node_id
        else:
            perticipant = sender
        tx_sender = [[tx.amount for tx in block.transactions
                      if tx.sender == perticipant]
                     for block in self.__chain]
        open_tx_sender = [tx.amount for tx in self.__open_transactions
                          if tx.sender == perticipant]
        tx_sender.append(open_tx_sender)
        balance_send = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0,
                              tx_sender, 0)

        tx_recipient = [[tx.amount for tx in block.transactions
                         if tx.recipient == perticipant]
                        for block in self.__chain]

        balance_rec = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0,
                             tx_recipient, 0)
        return balance_rec - balance_send

    def add_transaction(self, receipent, sender, signature, amount=1.0, is_receiving=False):
        """Add a Transaction"""  # Add Transaction
        if self.node_id is None:
            return False
        transaction = Transaction(sender, receipent, signature, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_file()
            if not is_receiving:
                for node in self.__peer_nodes:
                    url = 'http://{}/broadcast-transaction'.format(node)
                    try:
                        response = requests.post(url, json={'sender': sender, 'receipent': receipent, 'amount': amount,
                                                            'signature': signature})
                        if response.status_code == 400 or response.status_code == 500:
                            print('Transaction Declined')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False

    def mine_block(self):
        """Mining Blocks"""  # Mining
        if self.node_id is None:
            return None
        last_block = self.get_last_blockchain_value()
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        reward_transaction = Transaction('MINING', self.node_id, '', MINING_REWARD)
        copy_transaction = self.__open_transactions[:]
        for tx in copy_transaction:
            if not Wallet.verify_transaction(tx):
                return None
        copy_transaction.append(reward_transaction)

        block = Block(len(self.__chain), hashed_block, copy_transaction, proof)
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_file()
        for node in self.__peer_nodes:
            url = 'http://{}/broadcast-block'.format(node)
            try:
                converted_block = block.__dict__.copy()
                converted_block['transactions'] = [tx.__dict__ for tx in converted_block['transactions']]
                response = requests.post(url, json={'block' : converted_block})
                if response.status_code == 400 or response.status_code == 500:
                    print('Block Declined')
            except requests.exceptions.ConnectionError:
                continue
        return block

    def add_block(self, block):
        transactions = [Transaction(tx['sender'], tx['receipent'], tx['amount']) for tx in block['transactions']]
        proof_valid = Verification.valid_proof(transactions=transactions[:-1], last_hash=block['previous_hash'],
                                               proof=block['proof'])
        hash_match = hash_block(self.__chain[-1]) == block['previous_hash']

        if not proof_valid or hash_match:
            return False
        converted_block = Block(index=block['index'], previous_hash=block['previous_hash'], transactions=transactions,
                                proof=block['proof'], time=block['time'])
        self.__chain.append(converted_block)
        self.save_file()
        return True

    def add_nodes(self, node):
        self.__peer_nodes.add(node)
        self.save_file()

    def remove_node(self, node):
        self.__peer_nodes.discard(node)
        self.save_file()

    def get_nodes(self):
        return list(self.__peer_nodes)
