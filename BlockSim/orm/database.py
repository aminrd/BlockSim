import os
import sqlalchemy as db
from BlockSim import settings

class Database:
    def __init__(self, db_name='database.db'):
        db_fname = os.path.join(settings.root_dir, db_name)

        if os.path.exists(db_fname):
            self.engine = db.exists.