import sqlalchemy as db
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from BlockSim import settings
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)

    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="accounts", uselist=False)

    crypto_type = Column(String)
    balance = Column(Float, default=0.0)

    def __repr__(self):
        return f"Account (id:{self.id}, type={self.crypto_type}) [balance={self.balance}] ---> owner: {self.owner}]"

    def __str__(self):
        return self.__repr__()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    accounts = relationship("Account", order_by=Account.id, back_populates="owner")

    def __repr__(self):
        return f'User id: {self.id}'

    def __str__(self):
        return self.__repr__()

    def acc_count(self, crypto_type='all'):
        if crypto_type == 'all':
            return len(self.accounts)
        else:
            accs = list(filter(lambda a: a.crypto_type == crypto_type, self.accounts))
            return len(accs)


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    amount = Column(Float)
    time = Column(Integer, default=0)

    src = Column(Integer, ForeignKey('accounts.id'), nullable=True)
    dst = Column(Integer, ForeignKey('accounts.id'))

    source = relationship("Account", foreign_keys=[src])
    destination = relationship("Account", foreign_keys=[dst])

    def __repr__(self):
        return f'Transfer {self.amount} from {self.source} ---> {self.destination}'

    def __str__(self):
        return self.__repr__()


class Database:
    def __init__(self):
        self.engine = db.create_engine(settings.database_url,
                                       connect_args={'check_same_thread': False},
                                       echo=False)

        self.session = sessionmaker()
        self.session.configure(bind=self.engine)

        Base.metadata.create_all(self.engine)
        self.s = self.session()

    def add_objects(self, objects):
        self.s.add_all(objects)
        self.s.commit()
        return True

    def __del__(self):
        self.s.close()
        self.session.close_all()


if __name__ == '__main__':
    my_db = Database()
    u1 = User()
    a1 = Account(owner=u1, crypto_type="Bitcoin")
    my_db.s.add_all([u1, a1])

    u2 = User()
    a2 = Account(owner=u2, crypto_type="Bitcoin")
    my_db.s.add_all([u2, a2])

    my_db.s.commit()

    t = Transaction(amount=20.0, source=a1, destination=a2)
    my_db.s.add(t)

    my_db.s.commit()
    print('Database Initialized Successfully!')
