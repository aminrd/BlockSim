base_config = {
    'crypto_name': 'Bitcoin',
    'new_accounts': lambda t: 2000 + t // 10,
    'miner_gift': 6
}


class CointSimulator:
    def __init__(self, conf=None):
        if conf is None:
            conf = base_config

        self.config = conf
        self.accounts = []
