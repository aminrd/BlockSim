import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
database_url = f'sqlite:///{os.path.join(root_dir, "database.db")}'
