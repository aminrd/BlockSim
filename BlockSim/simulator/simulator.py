import random
from BlockSim.orm import database as db

base_config = {
    'crypto_name': 'Bitcoin',
    'new_accounts': lambda t: 2000 + t // 10,
    'miner_gift': 6
}


class CointSimulator:
    def __init__(self, conf=None):
        """
        Initializing a ConfigSimulator class designed to store each crypto type information
        such as accounts and transactions

        Parameters
        ----------
        conf: dict
            Config dictionary. Could be instantiated from BlockSim.simulator.simulator.base_config
        """
        self.turn_number = 0
        if conf is None:
            conf = base_config

        self.config = conf
        self.accounts = []
        self.transactions = []

    def get_update(self):
        return len(self.accounts), len(self.transactions)

    def turn(self, user_list=None, database=None):
        """
        Computes the next turn.

        Parameters
        ----------
        user_list: list
            List of users of type BlockSim.orm.database.User()

        database: BlockSim.orm.database.Database()
            Database object

        Returns
        -------
        update: tuple
            A tuple specifies (number of current users, number of current accounts)

        """
        self.turn_number += 1

        if user_list is None or database is None:
            update = self.get_update()
            return update

        if not isinstance(database, db.Database):
            raise TypeError('databse should be an instance of BlockSim.orm.database.Database()')

        n_account = self.config['new_accounts'](self.turn_number)
        new_accounts = [db.Account(owner=random.choice(user_list),
                        crypto_type=self.config.get('crypto_name', 'Bitcoin'))
                        for _ in range(n_account)]

        database.add_objects(new_accounts)
        self.accounts += new_accounts

        return self.get_update()
