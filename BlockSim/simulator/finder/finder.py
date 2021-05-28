from BlockSim.orm.database import Account, User, Database, Transaction
from collections import defaultdict, OrderedDict
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
        self.coins = coins

        for t in tqdm(range(turn_number), desc="Reading transactions: "):
            transactions = db.s.query(Transaction).filter_by(time=t).all()

            for trx in transactions:
                c_type = trx.destination.crypto_type
                balances[c_type][trx.dst] += trx.amount

                if trx.src is not None:
                    balances[c_type][trx.src] += trx.amount

        self.balances = balances

    def find(self, ratios):
        """
        Run the finder algorithm to find the account with highest probability given steak
        percentages for each crypto coin type.

        Parameters
        ----------
        ratios: dict
            ratios should be a dictionary mapping crypto names to steak percentage!

        Returns
        -------
        result: dict
            A dictionary mapping crypto_type to account id

        """
        if not isinstance(ratios, dict):
            return TypeError("ratios should be a dictionary mapping crypto names to steak percentage!")

        # Sort coins from smallest number of accounts to largest
        coin_order = sorted((len(self.balances[c], c)) for c in self.coins)

        # Sort accounts within each crypto-currency by balance
        sorted_balances = OrderedDict()
        for _, c in coin_order:
            sorted_balances[c] = sorted((balance, a_id) for a_id, balance in self.balances[c])



if __name__ == '__main__':
    from pprint import pprint
    finder = Finder(5)
    pprint(finder)
    print('Done!')
