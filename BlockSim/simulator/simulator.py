import random
from BlockSim.orm import database as db

base_config = {
    'crypto_name': 'Bitcoin',
    'new_accounts': lambda t: 2000 + t // 10,
    'transaction_function': lambda t: 0.5 + t / (t+100),
    'miner_gift': 6.25
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
        self.transactions = []

    def get_update(self):
        return len(self.accounts), len(self.transactions)

    def commit_transaction(self, src, dst):
        """
        Commint a transaction from src to dst. The amount is chosen by a random number times balance of the
        source account deducting the src.balance and deposit it to dst.balance.

        Parameters
        ----------
        src: BlockSim.orm.database.Account()
            Source account
        dst: BlockSim.orm.database.Account()
            Destination account

        Returns
        -------
        status: bool
            True if transaction was successful, False otherwise
        """
        if src.balance <= 0:
            return False

        if src.id == dst.id:
            return False

        src_account = self.database.session.query(db.Account).get(src.id)
        dst_account = self.database.session.query(db.Account).get(dst.id)

        amount = random.random() * src_account.balance
        src_account.balance = src_account.balance - amount
        dst_account.balance = dst_account.balance + amount
        self.database.session.commit()

        trx = db.Transaction(amount=amount, source=src_account,
                             destination=dst_account, time=self.turn_number)
        self.database.add_objects([trx])
        self.transactions.append(trx)
        return True

    def turn(self, user_list=None):
        """
        Computes the next turn.

        Parameters
        ----------
        user_list: list
            List of users of type BlockSim.orm.database.User()

        Returns
        -------
        update: tuple
            A tuple specifies (number of current users, number of current accounts)

        """
        self.turn_number += 1

        if user_list is None:
            update = self.get_update()
            return update

        n_account = self.config['new_accounts'](self.turn_number)
        new_accounts = [db.Account(owner=random.choice(user_list),
                        crypto_type=self.config.get('crypto_name', 'Bitcoin'))
                        for _ in range(n_account)]

        self.database.add_objects(new_accounts)
        self.accounts += new_accounts

        # Miner gift
        miner = random.choice(self.accounts)
        miner_db = self.database.session.query(db.Account).get(miner.id)
        miner_db.balance = miner_db + self.config.get('miner_gift', 6.25)
        self.database.session.commit()

        n_trx = self.config['transaction_function'](self.turn_number) * len(self.accounts)

        sources = random.choice(self.accounts, k=int(n_trx))
        destinations = random.choice(self.accounts, k=int(n_trx))
        for s, d in zip(sources, destinations):
            self.commit_transaction(s, d)

        return self.get_update()
