from BlockSim.orm.database import Account, User, Database, Transaction
from collections import defaultdict, OrderedDict
from tqdm import tqdm


def binary_find(balance, balances):
    left_idx, right_idx = 0, len(balances) - 1

    if balances[0][0] > balance or balances[-1][0] < balance:
        return []

    while right_idx > left_idx:
        index = (right_idx + left_idx) // 2
        sub = balances[index][0]

        # Found on left
        if balances[left_idx][0] == balance:
            i, ind = left_idx, []
            while i <= right_idx and balances[i][0] == balance:
                ind.append(i)
                i += 1
            return [balances[i] for i in ind]

        # Found on middle
        elif sub == balance:
            i, j, ind = index, index+1, []

            while i >= left_idx and balances[i][0] == balance:
                ind.append(i)
                i -= 1

            while j <= right_idx and balances[j][0] == balance:
                ind.append(j)
                j += 1

            return [balances[i] for i in ind]

        # Found on right
        elif balances[right_idx] == balance:
            i, ind = right_idx, []
            while i >= left_idx and balances[i][0] == balance:
                ind.append(i)
                i -= 1
            return [balances[i] for i in ind]

        elif sub > balance:
            if right_idx == index:
                indices = sorted([right_idx, left_idx])
                return [balances[ind] for ind in indices]
            right_idx = index
        else:
            if left_idx == index:
                indices = sorted([right_idx, left_idx])
                return [balances[ind] for ind in indices]
            left_idx = index

    indices = sorted([right_idx, left_idx])
    i, j = indices[0] - 1, indices[1]+1
    v1, v2 = balances[indices[0]-1][0], balances[indices[1]+1][0]

    while i >= 0 and balances[i][0] == v1:
        indices.append(i)
        i -= 1

    while j < len(balances) and balances[j][0] == v2:
        indices.append(j)
        j += 1

    return [balances[i] for i in indices]


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

        if sum(v for v in ratios.values()) != 1:
            raise ValueError("Sum of the steak values in ratios should be equal to 1.0!")

        # Sort coins from smallest number of accounts to largest
        coin_order = sorted((len(self.balances[c], c)) for c in self.coins)

        # Sort accounts within each crypto-currency by balance
        sorted_balances = OrderedDict()
        for _, c in coin_order:
            sorted_balances[c] = sorted((balance, a_id) for a_id, balance in self.balances[c])


if __name__ == '__main__':
    from pprint import pprint
    import random

    finder = Finder(5)
    pprint(finder.balances)

    balances = [(random.randrange(0, 10000), i) for i in range(1000)]
    balances = sorted(balances)
    result = binary_find(10, balances)

    print('Done!')
