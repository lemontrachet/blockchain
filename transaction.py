from collections import namedtuple


Transaction = namedtuple("Transaction", "sender recipient amount".split())
Wallet = namedtuple("Wallet", "ident".split())