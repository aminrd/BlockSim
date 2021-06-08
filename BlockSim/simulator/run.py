from BlockSim.simulator.simulator import CointSimulator
from BlockSim.orm.database import Database, User
from BlockSim.settings import root_dir
import BlockSim.config_files as cf
from tqdm import tqdm
import json
import os


def array2func(arr):
    def func(t):
        return sum(a * t ** p for p, a in enumerate(arr))

    return func


def load_configs():
    with open(os.path.join(cf.__path__._path[0], 'coins.json')) as f:
        jdata = json.load(f)

    configs = []
    for k, v in jdata.items():
        cfg = v
        for attr, farr in cfg.items():
            cfg[attr] = array2func(farr)

        cfg['crypto_name'] = k
        configs.append(cfg)

    return configs


def new_user_at_turn(t):
    return 100 + t


def setup(max_turn=1000, n_coins=3, verbose=False):
    configs = load_configs()

    if len(configs) < n_coins:
        raise ImportError("Not enough configs found in BlockSim.config_files.coins.json "
                          f"[found {len(configs)} configs] [But asked n_coins={n_coins}]")

    configs = configs[:n_coins]

    if os.path.exists(os.path.join(root_dir, 'database.db')):
        os.remove(os.path.join(root_dir, 'database.db'))

    db = Database()

    all_users = []
    simulators = [CointSimulator(conf=cfg, database=db) for cfg in configs]

    flushable_objects = []
    for t in tqdm(range(max_turn), desc="Simulating "):
        new_users = [User() for _ in range(new_user_at_turn(t))]
        all_users += new_users
        flushable_objects += new_users

        for simulator in simulators:
            if verbose:
                print(f'>{simulator.config["crypto_name"]}')

            new_objects = simulator.turn(user_list=all_users, verbose=verbose)
            flushable_objects += new_objects

        if len(flushable_objects) > 4096:
            db.add_objects(flushable_objects)
            flushable_objects = []

    db.s.close()


if __name__ == '__main__':
    setup(max_turn=10000, n_coins=5, verbose=False)
    print('Done!')
