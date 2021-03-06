import random
from BlockSim.orm import database as db

base_config = {
    'crypto_name': 'Bitcoin',
    'new_accounts': lambda t: 25 + t // 10,
    'miner_gift': lambda t: 6.25
}


class CointSimulator:
    def __init__(self, conf=None, database=None):
        """
        Initializing a ConfigSimulator class designed to store each crypto type information
        such as accounts and transactions

        Parameters
        ----------
        conf: dict
            Config dictionary. Could be instantiated from BlockSim.simulator.simulator.base_config

        database: BlockSim.orm.database.Database()
            Database object
        """
        self.turn_number = 0

        if not isinstance(database, db.Database):
            raise TypeError('Database should be an instance of BlockSim.orm.database.Database()')

        if conf is None:
            conf = base_config

        self.config = conf
        self.database = database
        self.accounts = []

    def get_update(self):
        return len(self.accounts)

    def commit_transaction(self, src_index, dst_index):
        """
        Commint a transaction from src to dst. The amount is chosen by a random number times balance of the
        source account deducting the src.balance and deposit it to dst.balance.

        Parameters
        ----------
        src_index: BlockSim.orm.database.Account()
            Source account index in list self.accounts
        dst_index: BlockSim.orm.database.Account()
            Destination account index in list self.accounts

        Returns
        -------
        trx: BlockSim.orm.database.Trasnaction()
            If everything goes well, returns the transaction. None otherwise.
        """
        src = self.accounts[src_index]
        dst = self.accounts[dst_index]

        if src.id == dst.id:
            return None

        src_account = src
        dst_account = dst

        # In some random cases, flushes the account to have empty balance
        if random.random() < 0.05:
            amount = src_account.balance
        else:
            amount = round(random.random() * src_account.balance, 8)

        if amount > 0:
            src_account.balance = round(src_account.balance - amount, 8)
            dst_account.balance = round(dst_account.balance + amount, 8)

            trx = db.Transaction(amount=amount, source=src_account,
                                 destination=dst_account, time=self.turn_number)
            return trx

        return None

    def turn(self, user_list=None, verbose=False):
        """
        Computes the next turn.

        Parameters
        ----------
        user_list: list
            List of users of type BlockSim.orm.database.User()

        verbose: bool
            Verbose printing details

        Returns
        -------
        new_db_objects: list
            A list of new objects that should be added to the database
        """
        self.turn_number += 1

        if user_list is None:
            update = self.get_update()
            return update

        n_account = int(self.config['new_accounts'](self.turn_number))

        cname = self.config.get('crypto_name', 'all')
        u_list = list(filter(lambda u: u.acc_count(cname) < 1, user_list))
        new_accounts = [db.Account(owner=random.choice(u_list), balance=0.0,
                                   crypto_type=self.config.get('crypto_name', 'Bitcoin'))
                        for _ in range(n_account)]

        self.accounts += new_accounts

        # Miner gift
        miner_db = random.choice(self.accounts)

        miner_gift = self.config.get('miner_gift')(self.turn_number)
        miner_db.balance = miner_db.balance + miner_gift

        miner_trx = db.Transaction(amount=miner_gift, source=None,
                                   destination=miner_db, time=self.turn_number)

        non_zero_accounts = [idx for idx, acc in enumerate(self.accounts) if acc.balance > 0]
        n_trx = random.randint(0, len(self.accounts))

        src_index = random.choices(non_zero_accounts, k=int(n_trx))
        dst_index = random.choices(list(range(len(self.accounts))), k=int(n_trx))

        new_transactions = []
        for i, (s, d) in enumerate(zip(src_index, dst_index)):
            if verbose:
                print(f'({self.config["crypto_name"]}) TRX: from {s} --> {d} [{i} out of {n_trx}]')

            new_trx = self.commit_transaction(s, d)
            if new_trx is not None:
                new_transactions.append(new_trx)

        new_db_objects = new_accounts + new_transactions + [miner_trx]
        return new_db_objects
