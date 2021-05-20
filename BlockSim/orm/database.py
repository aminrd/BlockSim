import os
import sqlalchemy as db
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from BlockSim import settings

Base = declarative_base()


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    owner = relationship("User", back_populates="accounts")

    crypto_type = Column(String)
    balance = Column(Integer, primary_key=True, default=0)

    def __repr__(self):
        return f"Account (id:{self.id}, type={self.crypto_type}) [balance={self.balance}] ---> owner: {self.owner}]"

    def __str__(self):
        return self.__repr__()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    accounts = relationship("Account", back_populates="owner")

    def __repr__(self):
        return f'User id: {self.id}'

    def __str__(self):
        return self.__repr__()


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    amount = Column(Integer, primary_key=True)

    source = relationship("Account")
    destination = relationship("Account")

    def __repr__(self):
        return f'Transfer {self.amount} from {self.source} ---> {self.destination}'

    def __str__(self):
        return self.__repr__()


class Database:
    def __init__(self, db_name='database.db'):
        db_fname = os.path.join(settings.root_dir, db_name)

        self.engine = db.create_engine('sqlite:///:memory:', echo=True)

        Base.metadata.create_all(self.engine)
