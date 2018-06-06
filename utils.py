import time
import random
from queue import Queue
import threading
from chain import Chain
from block import Block
from transaction import Transaction, Wallet



def make_transactions(q):
    wallets = [Wallet(x) for x in "B C D E F G H I J K".split()]
    wallets.append(Wallet("A"))
    while True:
        time.sleep(random.randint(2, 16))
        sender, recipient = random.sample(wallets, 2)
        amount = random.randint(1, 25)
        t = Transaction(sender, recipient, amount)
        q.put(t)


def validate_transaction(transaction, chain):
    """takes a Transaction-namedtuple and a Chain object,
    checks whether the sender has funds at least equal to the amount.
    Returns boolean"""
    target, sender = transaction.amount, transaction.sender.ident
    all_data = [block.data for block in chain.chain]
    if not all_data:
        return False
    # iterate backwards through data until sufficient funds found
    accum = 0
    #print("checking transaction: {} from {} to {}".format(target, sender, transaction.recipient.ident))
    for data in reversed(all_data):
        for trans in data:
            if trans.sender.ident == sender:
                accum -= trans.amount
            if trans.recipient.ident == sender:
                accum += trans.amount
            if accum >= target:
                #print("{} funds: {}".format(sender, accum))
                return True
    print("{} has insufficient funds: {}".format(sender, accum))
    return False


def run(q, transaction_q):
    while True:
        time.sleep(1)
        try:
            transaction = q.get()
        except:
            continue
        print("validating transaction:", transaction)
        print("transaction INVALID") if not validate_transaction(transaction, chain) else print("transaction VALID")
        transaction_q.put(transaction)




if __name__ == '__main__':
    q = Queue()
    gb = Block.make_genesis_block()
    chain = Chain()
    chain.chain.append(gb)
    print(chain.chain)
    thread1 = threading.Thread(target=make_transactions,
                               args=(q,))
    thread2 = threading.Thread(target=run, args=(q,))
    thread1.start()
    thread2.start()