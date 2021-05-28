from BlockSim.orm.database import Account, User, Database, Transaction
from collections import defaultdict
from tqdm import tqdm


class Finder:
    def __init__(self, turn_number, coins='all'):
        db = Database()
        available_coins = set(acc.crypto_type for acc in db.s.query(Account).all())

        if isinstance(coins, str) and coins == 'all':
            coins = list(available_coins)
        else:
            if any(c not in available_coins for c in coins):
                raise NameError(f"One/More of the coins in the list were not found in database!")

        balances = {k: defaultdict(float) for k in coins}

        for t in tqdm(range(turn_number), desc="Reading transactions: "):
            transactions = db.s.query(Transaction).filter_by(time=t).all()

            for trx in transactions:
                c_type = trx.destination.crypto_type
                balances[c_type][trx.dst] += trx.amount

                if trx.src is not None:
                    balances[c_type][trx.src] += trx.amount

        self.balances = balances


if __name__ == '__main__':
    from pprint import pprint
    finder = Finder(5)
    pprint(finder)
    print('Done!')
