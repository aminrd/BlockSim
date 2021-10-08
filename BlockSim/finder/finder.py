from BlockSim.orm.database import Account, Database, Transaction, User
from BlockSim.finder.classes import FinderAccount, FinderAnswer, FinderAnswerPaper
from collections import defaultdict, OrderedDict
from tqdm import tqdm
import warnings
import itertools
import copy


def binary_find(balance, all_balances):
    """
    Find all accounts having equal balance to target balance or close balance.

    Parameters
    ----------
    balance: BlockSim.finder.classes.FinderAccount()
        Target balance

    all_balances: list
        List of balances of type BlockSim.finder.classes.FinderAccount()

    Returns
    -------
    l: list
        List of accounts of tuples (balance_c, id_c)
    """
    if not isinstance(balance, FinderAccount):
        return TypeError("balance should be an instance of BlockSim.finder.classes.FinderAccount()")

    if not isinstance(all_balances, list) or not all(isinstance(x, FinderAccount) for x in all_balances):
        return TypeError("all_balances is a list of balances of type BlockSim.finder.classes.FinderAccount()")

    left_idx, right_idx = 0, len(all_balances) - 1

    if all_balances > balance or all_balances[-1] < balance:
        return []

    while right_idx > left_idx:
        index = (right_idx + left_idx) // 2
        sub = all_balances[index]

        # Found on left
        if all_balances[left_idx] == balance:
            i, ind = left_idx, []
            while i <= right_idx and all_balances[i] == balance:
                ind.append(i)
                i += 1
            return [all_balances[i] for i in ind]

        # Found on middle
        elif sub == balance:
            i, j, ind = index, index + 1, []

            while i >= left_idx and all_balances[i] == balance:
                ind.append(i)
                i -= 1

            while j <= right_idx and all_balances[j] == balance:
                ind.append(j)
                j += 1

            return [all_balances[i] for i in ind]

        # Found on right
        elif all_balances[right_idx] == balance:
            i, ind = right_idx, []
            while i >= left_idx and all_balances[i] == balance:
                ind.append(i)
                i -= 1
            return [all_balances[i] for i in ind]

        elif sub > balance:
            if right_idx == index:
                indices = sorted([right_idx, left_idx])
                return [all_balances[ind] for ind in indices]
            right_idx = index
        else:
            if left_idx == index:
                indices = sorted([right_idx, left_idx])
                return [all_balances[ind] for ind in indices]
            left_idx = index

    indices = sorted([right_idx, left_idx])
    i, j = indices[0] - 1, indices[1] + 1
    v1, v2 = all_balances[indices[0] - 1], all_balances[indices[1] + 1]

    while i >= 0 and all_balances[i] == v1:
        indices.append(i)
        i -= 1

    while j < len(all_balances) and all_balances[j] == v2:
        indices.append(j)
        j += 1

    return [all_balances[i] for i in indices]


def confidence_level(target, value):
    return max(0.0, 1 - abs(value - target) / target)


def check_finder_condition(ratios):
    if not isinstance(ratios, dict):
        return TypeError("ratios should be a dictionary mapping crypto names to steak percentage!")

    sum_values = sum(v for v in ratios.values())
    if abs(sum_values - 1.0) > 0.02:
        warnings.warn("Sum of the steak values in ratios should be equal to 1.0!")

    if any(v < 0 or v > 1 for v in ratios.values()):
        raise ValueError("Ratios should be greater than 0 and less than 1")

    if len(ratios.keys()) < 2:
        raise ValueError(f"Steak balances should have at least two steaks but given {len(ratios.keys())}")

class Finder:
    def __init__(self, turn_number, coins='all', synthetic=True):
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
                if c_type in self.coins:
                    balances[c_type][trx.dst] += trx.amount

                    if trx.src is not None:
                        balances[c_type][trx.src] += trx.amount

        self.balances = dict()
        for crypto_name, arr in balances.items():
            self.balances[crypto_name] = {k: v for k, v in arr.items() if v > 0}

        if synthetic:
            users = defaultdict(set)

            for acc_id, acc_balance in itertools.chain(*map(lambda x: x.items(), self.balances.values())):
                acc_db = db.s.query(Account).get(acc_id)
                users[acc_db.owner.id].add((acc_db.crypto_type, acc_balance, acc_id))

            self.users = users

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
        check_finder_condition(ratios)
        # Sort coins from smallest number of accounts to largest
        coin_order = sorted((len(self.balances[c]), c) for c in ratios.keys())

        # Sort accounts within each crypto-currency by balance
        sorted_balances = OrderedDict()
        for _, c in coin_order:
            sorted_balances[c] = sorted(FinderAccount(balance, a_id) for a_id, balance in self.balances[c].items())

        # Metric = (accuracy, variance)
        best_metric = (0, 1000)
        keys = list(sorted_balances.keys())
        answers = []

        for acc in tqdm(sorted_balances[keys[0]], desc='Running reverse finder method'):
            a_test = copy.deepcopy(acc)
            a_test.cl = 1.0
            answer = {keys[0]: [a_test]}

            for k_index in range(1, len(keys)):
                k_prev, k_current = keys[k_index - 1], keys[k_index]

                upcoming_answers = defaultdict(bool)
                for acc_prev in answer[k_prev]:
                    target_balance = acc_prev.balance * ratios[k_current] / ratios[k_prev]
                    target_acc = FinderAccount(target_balance, -1)
                    acc_list = copy.deepcopy(binary_find(target_acc, sorted_balances[k_current]))

                    for acc_found in acc_list:
                        acc_found.cl = acc_prev.cl * confidence_level(target_acc.balance, acc_found.balance)

                    acc_list = list(filter(lambda x: x.cl > 0.0, acc_list))
                    for recent_account in acc_list:
                        if upcoming_answers[recent_account.identifier]:
                            upcoming_answers[recent_account.identifier].cl += recent_account.cl
                        else:
                            upcoming_answers[recent_account.identifier] = recent_account
                        upcoming_answers[recent_account.identifier].voters += 1

                answer[k_current] = [v for v in upcoming_answers.values()]

            answers.append(FinderAnswer(answer))

        answers = sorted(answers, reverse=True)
        return answers[0]

    def find_paper(self, ratios, st=-1):
        """
        Run the finder algorithm to find the account with highest probability given steak
        percentages for each crypto coin type.
        Source: Arxive paper

        Parameters
        ----------
        ratios: dict
            ratios should be a dictionary mapping crypto names to steak percentage!

        st: float
            Score threshold

        Returns
        -------
        result: dict
            A dictionary mapping crypto_type to account id
        """
        if len(steak.keys()) < 2:
            return None

        check_finder_condition(ratios)
        coin_order = sorted((len(self.balances[c]), c) for c in ratios.keys())

        # Sort accounts within each crypto-currency by balance
        sorted_balances = OrderedDict()
        for _, c in coin_order:
            sorted_balances[c] = sorted(FinderAccount(balance, a_id) for a_id, balance in self.balances[c].items())

        best_score = -1
        best_answer = None
        keys = list(sorted_balances.keys())
        for acc in tqdm(sorted_balances[keys[0]], desc='Running reverse finder method'):
            answers = [[acc]]

            for i in range(2, len(keys)):
                target_balance = acc.balance * ratios[keys[i]] / ratios[keys[0]]
                target_acc = FinderAccount(target_balance, -1)
                acc_list = binary_find(target_acc, sorted_balances[keys[i]])
                answers.append(acc_list)

            for ans in itertools.product(*answers):
                new_ans = FinderAnswerPaper({k: a for k,a in zip(keys, ans)}, ratios)
                if new_ans.get_score() > best_score:
                    best_answer = new_ans

        return best_answer


if __name__ == '__main__':
    print('Testing BlockSim.finder module')
    from pprint import pprint
    import random

    finder = Finder(20)
    pprint(finder.balances)
    pprint(finder.users)

    balances = [random.randrange(0, 10000) for _ in range(1000)]
    balances = [FinderAccount(b, i) for i, b in enumerate(balances)]
    balances = sorted(balances)

    target_acc = FinderAccount(100, -1)
    result = binary_find(target_acc, balances)
    pprint(result)

    tot_cnt, hit_cnt = defaultdict(int), defaultdict(int)

    for u in finder.users.keys():
        test_case = finder.users[u]
        all_money = sum(b for _, b, _ in test_case)
        steak = {cname: balance / all_money for cname, balance, _ in test_case}

        print(f'Query : find user {test_case} with steak holding: ')
        print(steak)
        print('=' * 30)
        method = 'paper'

        n_acc = len(test_case)
        tot_cnt[n_acc] += 1

        if method == 'paper':
            f_result = finder.find_paper(steak)
        else:
            f_result = finder.find(steak)

        if f_result:
            uids_user = set(uid for _, _, uid in test_case)
            uids_ans = set(v.identifier for v in f_result.d.values())

            if any(v in uids_user for v in uids_ans):
                hit_cnt[n_acc] += 1

    with open('../result.txt', 'w') as f:
        f.write('--- total counter ---')
        f.write(pprint.pformat(tot_cnt, indent=4))
        f.write('--- hit counter ---')
        f.write(pprint.pformat(hit_cnt, indent=4))

    print('Done!')
