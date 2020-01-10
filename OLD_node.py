from blockchain import Blockchain
from uuid import uuid4
from wallet import Wallet
from utility.verification import Verification


class Node:
    def __init__(self):
        self.waiting_for_input = True
        # self.id = str(uuid4())
        self.wallet = Wallet()
        self.wallet.create_keys()
        self.blockchain = Blockchain(self.wallet.public_key)

    def get_transaction_value(self):
        """Transaction input"""  # Transaction input
        # tx_sender = input("Sender:")
        tx_receipent = input("Recipient: ")
        tx_amount = float(input("Amount: "))
        return tx_receipent, tx_amount

    def get_user_choice(self):
        """User Chjoice"""  # User Choice
        return input("Your Choice ")

    def UI(self):
        while self.waiting_for_input:
            print('Enter Choice')
            print('1:Add transaction')
            print('2:Mine bLock')
            print('3: Create Wallet')
            print('4: Check Transaction valididty: ')
            print('5:Print bocks')
            print('6: Load Wallet')
            print('7: Save Keys')
            print("q:Quit")
            user_choice = self.get_user_choice()
            if user_choice == '1':
                tx_data = self.get_transaction_value()
                receipent, amount = tx_data
                signature = self.wallet.sign_transaction(self.wallet.public_key,receipent,amount)
                if self.blockchain.add_transaction(receipent=receipent, sender=self.wallet.public_key,signature=signature, amount=amount):
                    print("Successful")
                else:
                    print("Failed")
                # print(open_transaction)
            elif user_choice == '2':
                if not self.blockchain.mine_block():
                    print("Mining Failed")
            elif user_choice == '3':
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_choice == '4':
                if Verification.verify_transactions(self.blockchain.get_open_transaction(),
                                                    self.blockchain.get_balance):
                    print("Valid Transaction")
                else:
                    print("Invalid transaction")
            elif user_choice == '5':
                self.print_blockchain()
            elif user_choice == '6':
                self.wallet.load_keys()
                print('Loaded')
            elif user_choice == '7':
                if self.wallet.private_key is not None and self.wallet.public_key is not None:
                    self.wallet.save_keys()
                print('Saved')
            elif user_choice == 'q':
                self.waiting_for_input = False
            else:
                print("Invalid Choice")
            if not Verification.verify_chain(self.blockchain.get_chain()):
                print("Invalid Blockchain")
                break
            print('Balance of  {} : {:6.2f}'.format(self.wallet.public_key, self.blockchain.get_balance()))
        else:
            print("User Left")

    def print_blockchain(self):
        """Print Blockchain"""  # Print BlockChain
        for block in self.blockchain.get_chain():
            print("Outputting Block")
            print(block)
        else:
            print("-" * 20)


if __name__ == '__main__':
    node = Node()
    node.UI()
