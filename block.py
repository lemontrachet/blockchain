from datetime import datetime
import hashlib
from transaction import Transaction, Wallet


class Block:

    blocks = 1000000

    def __init__(self, prev_hash, data):
        self.timestamp = datetime.now()
        self.ident = Block.blocks + 1
        Block.blocks += 1
        self.prev_hash = prev_hash
        self.data = data
        # current block hash is the hash of the properties above and a valid nonce
        # once nonce is found, current hash and nonce can be set
        self._nonce = None
        self._hash = None
        #print("block created at {} with id {}".format(self.timestamp, self.ident))

    @property
    def nonce(self):
        return self._nonce

    @nonce.setter
    def nonce(self, val):
        self._nonce = val

    @property
    def current_hash(self):
        return self._hash

    @current_hash.setter
    def current_hash(self, val):
        try:
            assert self.nonce is not None
            self._hash = val
        except AssertionError:
            print("cannot set current hash without first setting nonce.")

    def __repr__(self):
        return "\n".join((str(x) for x in (self.ident, self.timestamp, self.data[:20], self.prev_hash, self.nonce))) \
               + "\n"

    @classmethod
    def make_genesis_block(cls):
        try:
            assert Block.blocks == 1000000
        except AssertionError:
            print("unable to create genesis block.")
            return
        data = [Transaction(Wallet("X"), Wallet("A"), 500)]
        gb = Block("0000", data)

        # find nonce for genesis block
        nonce = 0
        while True:
            block_as_string = "".join([str(x) for x in [gb.ident,
                                                        gb.timestamp,
                                                        gb.data,
                                                        gb.prev_hash]])
            composite = str(nonce) + block_as_string
            hasher = hashlib.sha256()
            hasher.update(composite.encode("utf-8"))
            current_hash = hasher.hexdigest()
            if current_hash[:4] == "0000":
                break
            nonce += 1

        gb.nonce = nonce
        gb.current_hash = current_hash
        print("made genesis block with hash {}".format(gb.current_hash))
        return gb



if __name__ == '__main__':
    gb = Block.make_genesis_block()
    b = Block("123", "this is just a test.")
    b1 = Block("456", "this is just a test 2.")