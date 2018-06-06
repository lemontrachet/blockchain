import hashlib
import random
import time
from queue import Empty
from copy import deepcopy
from block import Block
from utils import validate_transaction


class Miner:

    miners = 1000000
    verification_depth = 2
    chain_q = []

    def __init__(self, trans_q, lock, chain_q=None):
        self.miner_id = Miner.miners + 1
        self.trans_q = trans_q
        self.lock = lock
        if chain_q is not None:
            Miner.chain_q = chain_q
        print("new miner with id: {}.".format(self.miner_id))
        Miner.miners += 1

    def find_transactions(self, chain):
        transactions = []
        while True:
            try:
                t = self.trans_q.get_nowait()
            except Empty:
                continue
            if not validate_transaction(t, chain):
                #print("invalid:", t)
                continue
            print(self.miner_id, "found valid transaction:", t)
            transactions.append(t)
            if len(transactions) == 4:
                print("miner {} assembling transactions for new block: {}".format(self.miner_id, transactions))
                return transactions

    @staticmethod
    def _hash_block(block):
        block_as_string = "".join([str(x) for x in [block.nonce,
                                                    block.ident,
                                                    block.timestamp,
                                                    block.data,
                                                    block.prev_hash]])
        hasher = hashlib.sha256()
        hasher.update(block_as_string.encode("utf-8"))
        return hasher.hexdigest()

    @staticmethod
    def verify_chain(chain):
        if len(chain.chain) == 0:
            print("uninitialised chain.")
            return
        if len(chain.chain) == 1 and chain.chain[0].data == "genesis block.":
            return True
        for i in range(len(chain.chain) - 1):
            prev, current = chain.chain[i], chain.chain[i + 1]
            prev_hash_hard = prev.current_hash
            prev_hash_check = Miner._hash_block(prev)
            current_prev_hash_record = current.prev_hash
            if not prev_hash_hard == prev_hash_check == current_prev_hash_record:
                return
        return True

    def mine_block(self, chain, transactions):
        transactions_per_block = chain.transactions_per_block
        try:
            assert len(transactions) == transactions_per_block
        except AssertionError:
            print("blocks must consist of {} transactions.".format(transactions_per_block))
            return

        if not self.verify_chain(chain):
            print("invalid chain.")
            return

        # assemble new block from transactions
        last_block = chain.chain[-1]
        prev_hash = self._hash_block(last_block)
        new_block = Block(prev_hash, transactions)

        # find nonce for new block
        nonce = 0
        while True:
            block_as_string = "".join([str(x) for x in [new_block.ident,
                                                        new_block.timestamp,
                                                        new_block.data,
                                                        new_block.prev_hash]])
            composite = str(nonce) + block_as_string
            hasher = hashlib.sha256()
            hasher.update(composite.encode("utf-8"))
            current_hash = hasher.hexdigest()
            if current_hash[:5] == "00000":
                print("nonce found: {}".format(nonce))
                break
            nonce += 1

        new_block.nonce = nonce
        new_block.current_hash = current_hash
        return new_block

    def add_to_chain(self, chain, new_block):
        # check validity of the chain - multiple miners may cause blocks to be added out of order
        if chain.chain[-1].current_hash == new_block.prev_hash and new_block.current_hash[:5] == "00000":
            chain.chain.append(new_block)
            #print("miner {} added block {} to chain.".format(self.miner_id, new_block.ident))
            print("current working chain for miner {} is of length {}.".format(self.miner_id,
                                                                               len(chain.chain)))
            return chain

    def get_chain_from_q(self):
        valid_chains = [chain for chain in Miner.chain_q
                        if self.verify_chain(chain)]
        if valid_chains:
            copy_chains = deepcopy(valid_chains)
            # find longest valid chain to build on
            return sorted(copy_chains, key=lambda x: len(x.chain))[-1]
        else:
            print("no valid chains.")
            for chain in Miner.chain_q:
                print(chain, "\n")

    def run(self):
        while True:
            working_chain = self.get_chain_from_q()
            if not working_chain:
                continue
            transactions = self.find_transactions(working_chain)
            new_block = self.mine_block(working_chain, transactions)
            try:
                extended_chain = self.add_to_chain(working_chain, new_block)
                if extended_chain:
                    Miner.chain_q.append(extended_chain)
                    chain_limit = 8
                    # keep only the chain_limit longest chains
                    Miner.chain_q = sorted(Miner.chain_q,
                                           key=lambda x: len(x.chain))[-chain_limit:]
                    print("chains:", [len(ch.chain) for ch in Miner.chain_q])
            except Exception as e:
                print("ERROR:", e)
                print(working_chain)
                print(new_block)
                #continue

            time.sleep(random.randint(4, 8))
