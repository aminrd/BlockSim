from BlockSim.simulator.simulator import CointSimulator
from BlockSim.orm.database import Database, User
from tqdm import tqdm


def new_user_at_turn(t):
    return 10 + t


def run(max_turn=1000):
    db = Database()

    all_users = []
    bitcoin_simulator = CointSimulator(database=db)

    for t in tqdm(range(max_turn), desc="Simulating "):
        new_users = [User() for _ in range(new_user_at_turn(t))]
        all_users += new_users
        db.add_objects(new_users)

        bitcoin_simulator.turn(user_list=all_users)

    db.s.close()


if __name__ == '__main__':
    run(5)
    print('Done!')
