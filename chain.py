from collections import deque

class Chain:

    transactions_per_block = 4

    def __init__(self):
        self.chain = deque([])