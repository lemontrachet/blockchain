from queue import Queue
import threading
import itertools
from block import Block
from chain import Chain
from miner import Miner
from utils import make_transactions

chain_q = []

def run_network():
    q = Queue()
    gb = Block.make_genesis_block()
    chain = Chain()
    chain.chain.append(gb)
    chain_q.append(chain)
    lock = threading.Lock()
    transaction_threads = [threading.Thread(target=make_transactions, args=(q,))
                           for _ in range(16)]
    miners = [Miner(q, lock, chain_q) for _ in range(4)]
    miner_threads = [threading.Thread(target=m.run)
                     for m in miners]
    for x in [*itertools.chain(miner_threads, transaction_threads)]:
        x.start()
    for m in [*itertools.chain(miner_threads, transaction_threads)]:
        m.join()



if __name__ == '__main__':
    run_network()